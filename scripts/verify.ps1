[CmdletBinding()]
param(
    [string]$BackupPath = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$BackendRoot = Join-Path $ProjectRoot "backend"
$FrontendRoot = Join-Path $ProjectRoot "frontend"
$LogPath = Join-Path $ProjectRoot "verification-output.txt"
$StartingLocation = Get-Location
$TranscriptStarted = $false
$TemporaryBackupPath = $null

$OriginalEnvironment = @{
    APP_ENV = [Environment]::GetEnvironmentVariable("APP_ENV", "Process")
    DATABASE_URL = [Environment]::GetEnvironmentVariable("DATABASE_URL", "Process")
    SECRET_KEY = [Environment]::GetEnvironmentVariable("SECRET_KEY", "Process")
    TEST_DATABASE_URL = [Environment]::GetEnvironmentVariable("TEST_DATABASE_URL", "Process")
}

function Write-Step {
    param([string]$Message)

    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Assert-LastExitCode {
    param([string]$Message)

    if ($LASTEXITCODE -ne 0) {
        throw "$Message (exit code: $LASTEXITCODE)"
    }
}

function Invoke-NativeCapture {
    param(
        [scriptblock]$Command,
        [string]$FailureMessage
    )

    $PreviousErrorActionPreference = $ErrorActionPreference
    $ExitCode = 0

    try {
        # Windows PowerShell 5.1 represents redirected native stderr as
        # ErrorRecord objects. Alembic writes normal INFO logs to stderr, so
        # temporarily avoid treating those records as terminating errors.
        $ErrorActionPreference = "Continue"
        $Output = & $Command 2>&1 | ForEach-Object { $_.ToString() }
        $ExitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $PreviousErrorActionPreference
    }

    if ($ExitCode -ne 0) {
        throw "$FailureMessage (exit code: $ExitCode)"
    }

    return ($Output -join [Environment]::NewLine).Trim()
}

function Restore-ProcessEnvironment {
    foreach ($Entry in $OriginalEnvironment.GetEnumerator()) {
        $EnvironmentPath = "Env:$($Entry.Key)"

        if ($null -eq $Entry.Value) {
            Remove-Item $EnvironmentPath -ErrorAction SilentlyContinue
        }
        else {
            Set-Item $EnvironmentPath $Entry.Value
        }
    }
}

function Reset-VerificationDatabase {
    param(
        [string]$DatabaseName,
        [string]$DockerCommand
    )

    if (-not $DatabaseName.StartsWith("quoteflow_")) {
        throw "Refusing to reset unexpected database name: $DatabaseName"
    }

    & $DockerCommand compose exec -T postgres dropdb `
        -U quoteflow --if-exists --force $DatabaseName
    Assert-LastExitCode "Could not reset $DatabaseName"

    & $DockerCommand compose exec -T postgres createdb `
        -U quoteflow $DatabaseName
    Assert-LastExitCode "Could not create $DatabaseName"
}

try {
    Set-Location $ProjectRoot
    Start-Transcript -Path $LogPath -Force | Out-Null
    $TranscriptStarted = $true

    Write-Host "FlowOps local verification" -ForegroundColor Green
    Write-Host "Project: $ProjectRoot"
    Write-Host "Log: $LogPath"

    Write-Step "Checking required tools"

    $Docker = Get-Command docker.exe -ErrorAction SilentlyContinue
    if ($null -eq $Docker) {
        $Docker = Get-Command docker -ErrorAction SilentlyContinue
    }
    if ($null -eq $Docker) {
        throw "Docker was not found. Install and start Docker Desktop, then run this script again."
    }
    $DockerCommand = $Docker.Source

    $Git = Get-Command git.exe -ErrorAction SilentlyContinue
    if ($null -eq $Git) {
        $Git = Get-Command git -ErrorAction SilentlyContinue
    }
    if ($null -eq $Git) {
        throw "Git was not found. Install Git for Windows, then run this script again."
    }
    $GitCommand = $Git.Source

    $Npm = Get-Command npm.cmd -ErrorAction SilentlyContinue
    if ($null -eq $Npm) {
        $Npm = Get-Command npm -ErrorAction SilentlyContinue
    }
    if ($null -eq $Npm) {
        throw "npm was not found. Install the current Node.js LTS release, then run this script again."
    }
    $NpmCommand = $Npm.Source

    & $DockerCommand info *> $null
    Assert-LastExitCode "Docker Desktop is installed but is not running"

    & $DockerCommand compose version
    Assert-LastExitCode "Docker Compose is not available"

    Write-Step "Starting PostgreSQL and Redis"
    & $DockerCommand compose up -d postgres redis
    Assert-LastExitCode "Docker services could not be started"

    $PostgresReady = $false
    for ($Attempt = 1; $Attempt -le 30; $Attempt++) {
        & $DockerCommand compose exec -T postgres `
            pg_isready -U quoteflow -d quoteflow *> $null

        if ($LASTEXITCODE -eq 0) {
            $PostgresReady = $true
            break
        }

        Start-Sleep -Seconds 2
    }

    if (-not $PostgresReady) {
        throw "PostgreSQL did not become ready within 60 seconds."
    }

    Write-Step "Preparing the Python environment"
    $VenvPython = Join-Path $BackendRoot ".venv\Scripts\python.exe"

    if (-not (Test-Path $VenvPython)) {
        $PythonLauncher = Get-Command py.exe -ErrorAction SilentlyContinue
        if ($null -eq $PythonLauncher) {
            $PythonLauncher = Get-Command python.exe -ErrorAction SilentlyContinue
        }
        if ($null -eq $PythonLauncher) {
            throw "Python was not found. Install Python 3.12 or newer, then run this script again."
        }

        if ($PythonLauncher.Name -eq "py.exe") {
            & $PythonLauncher.Source -3 -m venv (Join-Path $BackendRoot ".venv")
        }
        else {
            & $PythonLauncher.Source -m venv (Join-Path $BackendRoot ".venv")
        }
        Assert-LastExitCode "The backend virtual environment could not be created"
    }

    & $VenvPython -m pip install -r (Join-Path $BackendRoot "requirements.txt")
    Assert-LastExitCode "Backend dependencies could not be installed"

    Write-Step "Rebuilding isolated verification databases"
    Reset-VerificationDatabase -DatabaseName "quoteflow_verify" -DockerCommand $DockerCommand
    Reset-VerificationDatabase -DatabaseName "quoteflow_test" -DockerCommand $DockerCommand

    $env:APP_ENV = "test"
    $env:SECRET_KEY = "quoteflow_local_verification_secret_key"
    $env:DATABASE_URL = `
        "postgresql+psycopg://quoteflow:quoteflow_password@localhost:5433/quoteflow_verify"

    Write-Step "Running clean PostgreSQL migrations"
    Set-Location $BackendRoot
    & $VenvPython -m alembic upgrade head
    Assert-LastExitCode "Alembic could not upgrade the clean verification database"

    $CurrentRevision = Invoke-NativeCapture `
        -Command { & $VenvPython -m alembic current } `
        -FailureMessage "Alembic could not read the current revision"
    Write-Host $CurrentRevision

    if ($CurrentRevision -notmatch "9c1f2e4a7b6d") {
        throw "Unexpected Alembic revision after upgrade: $CurrentRevision"
    }

    Write-Step "Running the complete backend test suite"
    $env:TEST_DATABASE_URL = `
        "postgresql+psycopg://quoteflow:quoteflow_password@localhost:5433/quoteflow_test"
    & $VenvPython -m pytest -q
    Assert-LastExitCode "Backend tests failed"

    if (-not [string]::IsNullOrWhiteSpace($BackupPath)) {
        Write-Step "Rehearsing the migration against the supplied SQL backup"
        $ResolvedBackupPath = (Resolve-Path -LiteralPath $BackupPath).Path

        if ([System.IO.Path]::GetExtension($ResolvedBackupPath) -ne ".sql") {
            throw "BackupPath must point to a .sql file."
        }

        $BackupForRestore = $ResolvedBackupPath
        $BackupBytes = [System.IO.File]::ReadAllBytes($ResolvedBackupPath)
        $BackupEncoding = $null

        if (
            $BackupBytes.Length -ge 2 -and
            $BackupBytes[0] -eq 0xFF -and
            $BackupBytes[1] -eq 0xFE
        ) {
            $BackupEncoding = [System.Text.Encoding]::Unicode
        }
        elseif (
            $BackupBytes.Length -ge 2 -and
            $BackupBytes[0] -eq 0xFE -and
            $BackupBytes[1] -eq 0xFF
        ) {
            $BackupEncoding = [System.Text.Encoding]::BigEndianUnicode
        }

        if ($null -ne $BackupEncoding) {
            Write-Host "Converting the UTF-16 SQL backup to UTF-8 for PostgreSQL"
            $BackupText = $BackupEncoding.GetString(
                $BackupBytes,
                2,
                $BackupBytes.Length - 2
            )
            $TemporaryBackupPath = [System.IO.Path]::GetTempFileName()
            $Utf8WithoutBom = New-Object System.Text.UTF8Encoding($false)
            [System.IO.File]::WriteAllText(
                $TemporaryBackupPath,
                $BackupText,
                $Utf8WithoutBom
            )
            $BackupForRestore = $TemporaryBackupPath
        }

        Reset-VerificationDatabase `
            -DatabaseName "quoteflow_backup_verify" `
            -DockerCommand $DockerCommand

        & $DockerCommand cp `
            $BackupForRestore `
            "quoteflow_postgres:/tmp/quoteflow_database_backup.sql"
        Assert-LastExitCode "The SQL backup could not be copied into the PostgreSQL container"

        & $DockerCommand compose exec -T postgres `
            psql -v ON_ERROR_STOP=1 `
            -U quoteflow `
            -d quoteflow_backup_verify `
            -f /tmp/quoteflow_database_backup.sql
        Assert-LastExitCode "The SQL backup could not be restored"

        $env:DATABASE_URL = `
            "postgresql+psycopg://quoteflow:quoteflow_password@localhost:5433/quoteflow_backup_verify"

        $BackupRevisionBefore = Invoke-NativeCapture `
            -Command { & $VenvPython -m alembic current } `
            -FailureMessage "Could not read the backup database revision"
        Write-Host "Backup revision before upgrade: $BackupRevisionBefore"

        if ($BackupRevisionBefore -notmatch "ffb6e2d756ba") {
            throw "The backup is not at the expected ffb6e2d756ba revision."
        }

        & $VenvPython -m alembic upgrade head
        Assert-LastExitCode "The backup migration rehearsal failed"

        $BackupRevisionAfter = Invoke-NativeCapture `
            -Command { & $VenvPython -m alembic current } `
            -FailureMessage "Could not read the upgraded backup revision"
        Write-Host "Backup revision after upgrade: $BackupRevisionAfter"

        if ($BackupRevisionAfter -notmatch "9c1f2e4a7b6d") {
            throw "The backup did not reach the expected migration revision."
        }

        $QuoteTableCount = Invoke-NativeCapture `
            -Command {
                & $DockerCommand compose exec -T postgres `
                    psql -U quoteflow -d quoteflow_backup_verify -tAc `
                    "SELECT count(*) FROM pg_tables WHERE schemaname = 'public' AND tablename IN ('quotes', 'quote_items');"
            } `
            -FailureMessage "Could not verify quote tables in the restored backup"

        if ($QuoteTableCount -ne "2") {
            throw "Expected two quote tables after backup migration, found: $QuoteTableCount"
        }
    }

    Write-Step "Validating the frontend"
    Set-Location $FrontendRoot
    & $NpmCommand ci
    Assert-LastExitCode "Frontend dependencies could not be installed"

    & $NpmCommand run lint
    Assert-LastExitCode "Frontend lint failed"

    & $NpmCommand run build
    Assert-LastExitCode "Frontend production build failed"

    Write-Step "Git working tree summary"
    Set-Location $ProjectRoot
    & $GitCommand status --short --branch
    Assert-LastExitCode "Git status could not be read"

    Write-Host ""
    Write-Host "ALL CHECKS PASSED" -ForegroundColor Green
    Write-Host "Send verification-output.txt if you want the full run reviewed."
}
catch {
    Write-Host ""
    Write-Host "VERIFICATION FAILED" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    throw
}
finally {
    if (
        $null -ne $TemporaryBackupPath -and
        (Test-Path -LiteralPath $TemporaryBackupPath)
    ) {
        Remove-Item -LiteralPath $TemporaryBackupPath -Force -ErrorAction SilentlyContinue
    }

    Restore-ProcessEnvironment
    Set-Location $StartingLocation

    if ($TranscriptStarted) {
        Stop-Transcript | Out-Null
    }
}
