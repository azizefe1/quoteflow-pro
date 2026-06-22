"use client";

import { FormEvent, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

import { getAccessToken } from "@/lib/auth";
import {
  CustomerResponse,
  createCustomer,
  deactivateCustomer,
  listCustomers,
} from "@/lib/customers";
import { WorkspaceShell } from "../_components/workspace-shell";

export default function CustomersPage() {
  const params = useParams<{ companyId: string }>();
  const router = useRouter();
  const companyId = params.companyId;

  const [customers, setCustomers] = useState<CustomerResponse[]>([]);
  const [search, setSearch] = useState("");
  const [name, setName] = useState("ABC Industrial Ltd.");
  const [contactName, setContactName] = useState("Ahmet Yilmaz");
  const [email, setEmail] = useState("contact@example.com");
  const [phone, setPhone] = useState("+90 555 111 22 33");
  const [taxNumber, setTaxNumber] = useState("1234567890");
  const [total, setTotal] = useState(0);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);

  useEffect(() => {
    const token = getAccessToken();

    if (!token) {
      router.push("/login");
      return;
    }

    listCustomers(token, companyId, {
      search: "",
      limit: 20,
      offset: 0,
    })
      .then((response) => {
        setCustomers(response.items);
        setTotal(response.total);
      })
      .catch((error: unknown) => {
        const message =
          error instanceof Error ? error.message : "Customers could not be loaded.";

        setErrorMessage(message);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [companyId, router]);

  async function loadCustomers(searchValue = search) {
    const token = getAccessToken();

    if (!token) {
      router.push("/login");
      return;
    }

    setErrorMessage("");
    setIsLoading(true);

    try {
      const response = await listCustomers(token, companyId, {
        search: searchValue,
        limit: 20,
        offset: 0,
      });

      setCustomers(response.items);
      setTotal(response.total);
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Customers could not be loaded.";

      setErrorMessage(message);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleCreateCustomer(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const token = getAccessToken();

    if (!token) {
      router.push("/login");
      return;
    }

    setErrorMessage("");
    setSuccessMessage("");
    setIsCreating(true);

    try {
      const customer = await createCustomer(token, companyId, {
        name,
        contact_name: contactName,
        email,
        phone,
        tax_number: taxNumber,
      });

      setCustomers((currentCustomers) => [customer, ...currentCustomers]);
      setTotal((currentTotal) => currentTotal + 1);
      setSuccessMessage(`${customer.name} created.`);
      setName("");
      setContactName("");
      setEmail("");
      setPhone("");
      setTaxNumber("");
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Customer could not be created.";

      setErrorMessage(message);
    } finally {
      setIsCreating(false);
    }
  }

  async function handleDeactivateCustomer(customerId: string) {
    const token = getAccessToken();

    if (!token) {
      router.push("/login");
      return;
    }

    setErrorMessage("");
    setSuccessMessage("");

    try {
      await deactivateCustomer(token, companyId, customerId);

      setCustomers((currentCustomers) =>
        currentCustomers.filter((customer) => customer.id !== customerId),
      );
      setTotal((currentTotal) => Math.max(currentTotal - 1, 0));
      setSuccessMessage("Customer deactivated.");
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Customer could not be deactivated.";

      setErrorMessage(message);
    }
  }

  return (
    <WorkspaceShell companyId={companyId}>
      <section className="grid gap-6 xl:grid-cols-[0.85fr_1.15fr]">
        <div className="rounded-[2rem] border border-white/10 bg-white/[0.05] p-6 shadow-2xl shadow-black/20">
          <p className="text-sm font-black uppercase tracking-[0.35em] text-cyan-300">
            Customers
          </p>

          <h2 className="mt-4 text-3xl font-black tracking-tight">
            Create customer
          </h2>

          <form className="mt-8 grid gap-4" onSubmit={handleCreateCustomer}>
            <TextInput label="Customer name" onChange={setName} value={name} />
            <TextInput label="Contact name" onChange={setContactName} value={contactName} />
            <TextInput label="Email" onChange={setEmail} type="email" value={email} />
            <TextInput label="Phone" onChange={setPhone} value={phone} />
            <TextInput label="Tax number" onChange={setTaxNumber} value={taxNumber} />

            <button
              className="rounded-2xl bg-cyan-400 px-5 py-4 text-sm font-black text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-60"
              disabled={isCreating}
              type="submit"
            >
              {isCreating ? "Creating customer..." : "Create customer"}
            </button>
          </form>

          {errorMessage ? (
            <div className="mt-5 rounded-2xl border border-red-400/20 bg-red-400/10 px-4 py-3 text-sm text-red-200">
              {errorMessage}
            </div>
          ) : null}

          {successMessage ? (
            <div className="mt-5 rounded-2xl border border-emerald-400/20 bg-emerald-400/10 px-4 py-3 text-sm text-emerald-200">
              {successMessage}
            </div>
          ) : null}
        </div>

        <div className="rounded-[2rem] border border-white/10 bg-white/[0.05] p-6 shadow-2xl shadow-black/20">
          <div className="flex flex-col justify-between gap-5 md:flex-row md:items-end">
            <div>
              <p className="text-sm font-black uppercase tracking-[0.35em] text-cyan-300">
                Customer list
              </p>
              <h2 className="mt-4 text-3xl font-black tracking-tight">
                {total} active customers
              </h2>
            </div>

            <form
              className="flex gap-3"
              onSubmit={(event) => {
                event.preventDefault();
                void loadCustomers(search);
              }}
            >
              <input
                className="w-full rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3 text-white outline-none transition focus:border-cyan-300 md:w-72"
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Search customers..."
                type="search"
                value={search}
              />
              <button
                className="rounded-2xl border border-white/10 px-5 py-3 text-sm font-black text-white transition hover:bg-white/10"
                type="submit"
              >
                Search
              </button>
            </form>
          </div>

          <div className="mt-8 grid gap-4">
            {isLoading ? (
              <div className="rounded-2xl border border-white/10 bg-slate-950/80 p-6 text-slate-400">
                Loading customers...
              </div>
            ) : customers.length === 0 ? (
              <div className="rounded-2xl border border-white/10 bg-slate-950/80 p-6 text-slate-400">
                No customers found.
              </div>
            ) : (
              customers.map((customer) => (
                <div
                  className="rounded-2xl border border-white/10 bg-slate-950/80 p-5"
                  key={customer.id}
                >
                  <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
                    <div>
                      <p className="text-xl font-black">{customer.name}</p>
                      <p className="mt-1 text-sm text-slate-400">
                        {customer.contact_name ?? "No contact"} • {customer.email ?? "No email"}
                      </p>
                      <p className="mt-3 text-sm text-slate-300">
                        {customer.phone ?? "No phone"} • Tax: {customer.tax_number ?? "-"}
                      </p>
                    </div>

                    <button
                      className="rounded-full border border-red-400/20 px-4 py-2 text-xs font-black uppercase tracking-[0.2em] text-red-200 transition hover:bg-red-400/10"
                      onClick={() => void handleDeactivateCustomer(customer.id)}
                      type="button"
                    >
                      Deactivate
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </section>
    </WorkspaceShell>
  );
}

function TextInput({
  label,
  onChange,
  type = "text",
  value,
}: {
  label: string;
  onChange: (value: string) => void;
  type?: string;
  value: string;
}) {
  return (
    <label className="block">
      <span className="text-sm font-bold text-slate-300">{label}</span>
      <input
        className="mt-2 w-full rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3 text-white outline-none transition focus:border-cyan-300"
        onChange={(event) => onChange(event.target.value)}
        type={type}
        value={value}
      />
    </label>
  );
}