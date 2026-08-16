"use client";

import { FormEvent, ReactNode, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

import { getAccessToken } from "@/lib/auth";
import {
  ProductListResponse,
  ProductResponse,
  createProduct,
  deactivateProduct,
  listProducts,
  updateProduct,
} from "@/lib/products";
import { WorkspaceShell } from "../_components/workspace-shell";

const PAGE_SIZE = 10;

type ProductFormValues = {
  sku: string;
  name: string;
  description: string;
  unit: string;
  unitPrice: string;
  currency: string;
  taxRate: string;
  stockQuantity: string;
};

type ProductEditState = {
  id: string;
  values: ProductFormValues;
};

const EMPTY_PRODUCT_FORM: ProductFormValues = {
  sku: "",
  name: "",
  description: "",
  unit: "piece",
  unitPrice: "0.00",
  currency: "TRY",
  taxRate: "20.00",
  stockQuantity: "0.00",
};

export default function ProductsPage() {
  const params = useParams<{ companyId: string }>();
  const router = useRouter();
  const companyId = params.companyId;

  const [products, setProducts] = useState<ProductResponse[]>([]);
  const [createForm, setCreateForm] = useState<ProductFormValues>({
    ...EMPTY_PRODUCT_FORM,
  });
  const [editState, setEditState] = useState<ProductEditState | null>(null);
  const [search, setSearch] = useState("");
  const [appliedSearch, setAppliedSearch] = useState("");
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [deactivatingProductId, setDeactivatingProductId] = useState<string | null>(
    null,
  );

  useEffect(() => {
    const token = getAccessToken();

    if (!token) {
      router.replace("/login");
      return;
    }

    let ignoreResponse = false;

    listProducts(token, companyId, {
      limit: PAGE_SIZE,
      offset: 0,
    })
      .then((response) => {
        if (ignoreResponse) {
          return;
        }

        setProducts(response.items);
        setTotal(response.total);
        setOffset(response.offset);
      })
      .catch((error: unknown) => {
        if (ignoreResponse) {
          return;
        }

        const message =
          error instanceof Error ? error.message : "Products could not be loaded.";

        setErrorMessage(message);
      })
      .finally(() => {
        if (!ignoreResponse) {
          setIsLoading(false);
        }
      });

    return () => {
      ignoreResponse = true;
    };
  }, [companyId, router]);

  async function loadProducts(
    searchValue = appliedSearch,
    nextOffset = offset,
  ): Promise<ProductListResponse | null> {
    const token = getAccessToken();

    if (!token) {
      router.replace("/login");
      return null;
    }

    setErrorMessage("");
    setIsLoading(true);

    try {
      const response = await listProducts(token, companyId, {
        search: searchValue,
        limit: PAGE_SIZE,
        offset: nextOffset,
      });

      setProducts(response.items);
      setTotal(response.total);
      setOffset(response.offset);

      return response;
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Products could not be loaded.";

      setErrorMessage(message);
      return null;
    } finally {
      setIsLoading(false);
    }
  }

  async function handleCreateProduct(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const token = getAccessToken();

    if (!token) {
      router.replace("/login");
      return;
    }

    setErrorMessage("");
    setSuccessMessage("");
    setIsCreating(true);

    try {
      const product = await createProduct(token, companyId, toProductPayload(createForm));

      setCreateForm({ ...EMPTY_PRODUCT_FORM });
      setEditState(null);
      setSuccessMessage(`${product.name} created.`);
      await loadProducts(appliedSearch, 0);
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Product could not be created.";

      setErrorMessage(message);
    } finally {
      setIsCreating(false);
    }
  }

  async function handleUpdateProduct(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!editState) {
      return;
    }

    const token = getAccessToken();

    if (!token) {
      router.replace("/login");
      return;
    }

    setErrorMessage("");
    setSuccessMessage("");
    setIsUpdating(true);

    try {
      const product = await updateProduct(
        token,
        companyId,
        editState.id,
        toProductPayload(editState.values),
      );

      setEditState(null);
      setSuccessMessage(`${product.name} updated.`);

      const response = await loadProducts(appliedSearch, offset);

      if (response && response.items.length === 0 && response.total > 0 && offset > 0) {
        const lastPageOffset = Math.floor((response.total - 1) / PAGE_SIZE) * PAGE_SIZE;
        await loadProducts(appliedSearch, lastPageOffset);
      }
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Product could not be updated.";

      setErrorMessage(message);
    } finally {
      setIsUpdating(false);
    }
  }

  async function handleDeactivateProduct(product: ProductResponse) {
    const confirmed = window.confirm(
      `Deactivate ${product.name}? It will no longer appear in active product lists.`,
    );

    if (!confirmed) {
      return;
    }

    const token = getAccessToken();

    if (!token) {
      router.replace("/login");
      return;
    }

    setErrorMessage("");
    setSuccessMessage("");
    setDeactivatingProductId(product.id);

    try {
      await deactivateProduct(token, companyId, product.id);

      if (editState?.id === product.id) {
        setEditState(null);
      }

      const nextOffset =
        products.length === 1 && offset > 0 ? Math.max(0, offset - PAGE_SIZE) : offset;

      await loadProducts(appliedSearch, nextOffset);
      setSuccessMessage(`${product.name} deactivated.`);
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Product could not be deactivated.";

      setErrorMessage(message);
    } finally {
      setDeactivatingProductId(null);
    }
  }

  const currentPage = Math.floor(offset / PAGE_SIZE) + 1;
  const pageCount = Math.max(Math.ceil(total / PAGE_SIZE), 1);
  const hasPreviousPage = offset > 0;
  const hasNextPage = offset + products.length < total;

  return (
    <WorkspaceShell companyId={companyId}>
      <div aria-live="polite" className="mb-6 grid gap-3">
        {errorMessage ? (
          <div className="rounded-2xl border border-red-400/20 bg-red-400/10 px-4 py-3 text-sm text-red-200">
            {errorMessage}
          </div>
        ) : null}

        {successMessage ? (
          <div className="rounded-2xl border border-emerald-400/20 bg-emerald-400/10 px-4 py-3 text-sm text-emerald-200">
            {successMessage}
          </div>
        ) : null}
      </div>

      <section className="grid gap-6 xl:grid-cols-[0.85fr_1.15fr]">
        <div className="rounded-[2rem] border border-white/10 bg-white/[0.05] p-6 shadow-2xl shadow-black/20">
          <p className="text-sm font-black uppercase tracking-[0.35em] text-cyan-300">
            Products
          </p>
          <h2 className="mt-4 text-3xl font-black tracking-tight">Create product</h2>
          <p className="mt-3 text-sm leading-6 text-slate-400">
            Add reusable catalog items with pricing, tax and stock information.
          </p>

          <form className="mt-8 grid gap-4" onSubmit={handleCreateProduct}>
            <ProductFields onChange={setCreateForm} values={createForm} />

            <button
              className="rounded-2xl bg-cyan-400 px-5 py-4 text-sm font-black text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-60"
              disabled={isCreating}
              type="submit"
            >
              {isCreating ? "Creating product..." : "Create product"}
            </button>
          </form>
        </div>

        <div className="rounded-[2rem] border border-white/10 bg-white/[0.05] p-6 shadow-2xl shadow-black/20">
          <div className="flex flex-col justify-between gap-5 md:flex-row md:items-end">
            <div>
              <p className="text-sm font-black uppercase tracking-[0.35em] text-cyan-300">
                Product catalog
              </p>
              <h2 className="mt-4 text-3xl font-black tracking-tight">
                {total} active {total === 1 ? "product" : "products"}
              </h2>
            </div>

            <form
              className="flex flex-col gap-3 sm:flex-row"
              onSubmit={(event) => {
                event.preventDefault();
                const normalizedSearch = search.trim();

                setAppliedSearch(normalizedSearch);
                setEditState(null);
                setSuccessMessage("");
                void loadProducts(normalizedSearch, 0);
              }}
            >
              <input
                aria-label="Search products"
                className="w-full rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-300 md:w-64"
                maxLength={120}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Name, SKU or description"
                type="search"
                value={search}
              />
              <button
                className="rounded-2xl border border-white/10 px-5 py-3 text-sm font-black text-white transition hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-60"
                disabled={isLoading}
                type="submit"
              >
                Search
              </button>
            </form>
          </div>

          {appliedSearch ? (
            <div className="mt-5 flex items-center gap-3 text-sm text-slate-400">
              <span>
                Results for <strong className="text-slate-200">“{appliedSearch}”</strong>
              </span>
              <button
                className="font-bold text-cyan-300 transition hover:text-cyan-200"
                onClick={() => {
                  setSearch("");
                  setAppliedSearch("");
                  setEditState(null);
                  void loadProducts("", 0);
                }}
                type="button"
              >
                Clear
              </button>
            </div>
          ) : null}

          <div className="mt-8 grid gap-4">
            {isLoading ? (
              <div className="rounded-2xl border border-white/10 bg-slate-950/80 p-6 text-slate-400">
                Loading products...
              </div>
            ) : products.length === 0 ? (
              <div className="rounded-2xl border border-white/10 bg-slate-950/80 p-6 text-slate-400">
                {appliedSearch
                  ? "No products match this search."
                  : "No active products yet. Create the first catalog item."}
              </div>
            ) : (
              products.map((product) => {
                const isEditing = editState?.id === product.id;
                const isDeactivating = deactivatingProductId === product.id;

                return (
                  <article
                    className="rounded-2xl border border-white/10 bg-slate-950/80 p-5"
                    key={product.id}
                  >
                    {isEditing && editState ? (
                      <form className="grid gap-4" onSubmit={handleUpdateProduct}>
                        <div className="flex items-center justify-between gap-4">
                          <div>
                            <p className="text-xs font-black uppercase tracking-[0.25em] text-cyan-300">
                              Edit product
                            </p>
                            <p className="mt-2 text-lg font-black">{product.name}</p>
                          </div>
                          <button
                            className="text-sm font-bold text-slate-400 transition hover:text-white"
                            disabled={isUpdating}
                            onClick={() => setEditState(null)}
                            type="button"
                          >
                            Cancel
                          </button>
                        </div>

                        <ProductFields
                          onChange={(values) =>
                            setEditState((currentState) =>
                              currentState ? { ...currentState, values } : currentState,
                            )
                          }
                          values={editState.values}
                        />

                        <button
                          className="rounded-2xl bg-cyan-400 px-5 py-3 text-sm font-black text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-60"
                          disabled={isUpdating}
                          type="submit"
                        >
                          {isUpdating ? "Saving changes..." : "Save changes"}
                        </button>
                      </form>
                    ) : (
                      <div className="grid gap-5">
                        <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-start">
                          <div className="min-w-0">
                            <div className="flex flex-wrap items-center gap-3">
                              <h3 className="text-xl font-black">{product.name}</h3>
                              <span className="rounded-full border border-white/10 px-3 py-1 text-xs font-bold text-slate-400">
                                {product.sku ?? "No SKU"}
                              </span>
                            </div>
                            <p className="mt-2 break-words text-sm leading-6 text-slate-400">
                              {product.description ?? "No description"}
                            </p>
                          </div>

                          <div className="flex shrink-0 gap-2">
                            <button
                              className="rounded-full border border-cyan-400/20 px-4 py-2 text-xs font-black uppercase tracking-[0.16em] text-cyan-200 transition hover:bg-cyan-400/10"
                              onClick={() =>
                                setEditState({
                                  id: product.id,
                                  values: toFormValues(product),
                                })
                              }
                              type="button"
                            >
                              Edit
                            </button>
                            <button
                              className="rounded-full border border-red-400/20 px-4 py-2 text-xs font-black uppercase tracking-[0.16em] text-red-200 transition hover:bg-red-400/10 disabled:cursor-not-allowed disabled:opacity-60"
                              disabled={isDeactivating}
                              onClick={() => void handleDeactivateProduct(product)}
                              type="button"
                            >
                              {isDeactivating ? "Deactivating..." : "Deactivate"}
                            </button>
                          </div>
                        </div>

                        <dl className="grid grid-cols-2 gap-3 md:grid-cols-4">
                          <ProductMetric
                            label="Unit price"
                            value={`${formatDecimal(product.unit_price)} ${product.currency}`}
                          />
                          <ProductMetric
                            label="Tax rate"
                            value={`%${formatDecimal(product.tax_rate)}`}
                          />
                          <ProductMetric
                            label="Stock"
                            value={formatDecimal(product.stock_quantity)}
                          />
                          <ProductMetric label="Unit" value={product.unit} />
                        </dl>
                      </div>
                    )}
                  </article>
                );
              })
            )}
          </div>

          <div className="mt-6 flex flex-col items-center justify-between gap-4 border-t border-white/10 pt-5 sm:flex-row">
            <p className="text-sm text-slate-400">
              Page {currentPage} of {pageCount}
            </p>
            <div className="flex gap-3">
              <button
                className="rounded-full border border-white/10 px-4 py-2 text-sm font-bold text-slate-300 transition hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-40"
                disabled={!hasPreviousPage || isLoading}
                onClick={() => {
                  setEditState(null);
                  void loadProducts(appliedSearch, Math.max(0, offset - PAGE_SIZE));
                }}
                type="button"
              >
                Previous
              </button>
              <button
                className="rounded-full border border-white/10 px-4 py-2 text-sm font-bold text-slate-300 transition hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-40"
                disabled={!hasNextPage || isLoading}
                onClick={() => {
                  setEditState(null);
                  void loadProducts(appliedSearch, offset + PAGE_SIZE);
                }}
                type="button"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      </section>
    </WorkspaceShell>
  );
}

function ProductFields({
  onChange,
  values,
}: {
  onChange: (values: ProductFormValues) => void;
  values: ProductFormValues;
}) {
  function updateField(field: keyof ProductFormValues, value: string) {
    onChange({ ...values, [field]: value });
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2">
      <Field label="Product name" spanColumns>
        <input
          className={fieldClassName}
          maxLength={180}
          minLength={2}
          onChange={(event) => updateField("name", event.target.value)}
          required
          type="text"
          value={values.name}
        />
      </Field>

      <Field label="SKU">
        <input
          className={fieldClassName}
          maxLength={80}
          onChange={(event) => updateField("sku", event.target.value)}
          placeholder="Optional"
          type="text"
          value={values.sku}
        />
      </Field>

      <Field label="Unit">
        <input
          className={fieldClassName}
          maxLength={40}
          minLength={1}
          onChange={(event) => updateField("unit", event.target.value)}
          required
          type="text"
          value={values.unit}
        />
      </Field>

      <Field label="Description" spanColumns>
        <textarea
          className={`${fieldClassName} min-h-24 resize-y`}
          onChange={(event) => updateField("description", event.target.value)}
          placeholder="Optional product details"
          value={values.description}
        />
      </Field>

      <Field label="Unit price">
        <input
          className={fieldClassName}
          min="0"
          onChange={(event) => updateField("unitPrice", event.target.value)}
          required
          step="0.01"
          type="number"
          value={values.unitPrice}
        />
      </Field>

      <Field label="Currency">
        <input
          className={`${fieldClassName} uppercase`}
          maxLength={3}
          minLength={3}
          onChange={(event) => updateField("currency", event.target.value.toUpperCase())}
          required
          type="text"
          value={values.currency}
        />
      </Field>

      <Field label="Tax rate (%)">
        <input
          className={fieldClassName}
          max="100"
          min="0"
          onChange={(event) => updateField("taxRate", event.target.value)}
          required
          step="0.01"
          type="number"
          value={values.taxRate}
        />
      </Field>

      <Field label="Stock quantity">
        <input
          className={fieldClassName}
          min="0"
          onChange={(event) => updateField("stockQuantity", event.target.value)}
          required
          step="0.01"
          type="number"
          value={values.stockQuantity}
        />
      </Field>
    </div>
  );
}

function Field({
  children,
  label,
  spanColumns = false,
}: {
  children: ReactNode;
  label: string;
  spanColumns?: boolean;
}) {
  return (
    <label className={spanColumns ? "block sm:col-span-2" : "block"}>
      <span className="text-sm font-bold text-slate-300">{label}</span>
      {children}
    </label>
  );
}

function ProductMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
      <dt className="text-xs font-bold uppercase tracking-[0.16em] text-slate-500">
        {label}
      </dt>
      <dd className="mt-2 break-words text-sm font-black text-slate-200">{value}</dd>
    </div>
  );
}

function toProductPayload(values: ProductFormValues) {
  return {
    sku: values.sku,
    name: values.name,
    description: values.description,
    unit: values.unit,
    unit_price: values.unitPrice,
    currency: values.currency,
    tax_rate: values.taxRate,
    stock_quantity: values.stockQuantity,
  };
}

function toFormValues(product: ProductResponse): ProductFormValues {
  return {
    sku: product.sku ?? "",
    name: product.name,
    description: product.description ?? "",
    unit: product.unit,
    unitPrice: product.unit_price,
    currency: product.currency,
    taxRate: product.tax_rate,
    stockQuantity: product.stock_quantity,
  };
}

function formatDecimal(value: string) {
  const numericValue = Number(value);

  if (!Number.isFinite(numericValue)) {
    return value;
  }

  return new Intl.NumberFormat("tr-TR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(numericValue);
}

const fieldClassName =
  "mt-2 w-full rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-300";
