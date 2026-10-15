"use client";

export function ThrowButton() {
  return (
    <button
      type="button"
      className="mt-4 rounded-control bg-navy-700 px-4 py-2 text-stone-0"
      onClick={() => {
        throw new Error("MON-01 frontend test exception");
      }}
    >
      Throw test error
    </button>
  );
}
