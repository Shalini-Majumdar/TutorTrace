import { Check } from 'lucide-react';

export default function AnswerOption({
  option,
  index,
  selected,
  onSelect,
  disabled,
}) {
  const letter =
    String.fromCharCode(
      65 + index
    );

  return (
    <button
      type="button"
      onClick={() =>
        onSelect(option.id)
      }
      disabled={disabled}
      aria-pressed={selected}
      className={`group flex w-full items-center gap-3 rounded-xl border-2 px-4 py-3.5 text-left transition-all duration-150 focus:outline-none focus-visible:ring-2 focus-visible:ring-cobalt-400 focus-visible:ring-offset-1 disabled:cursor-not-allowed ${
        selected
          ? 'border-cobalt-500 bg-cobalt-50'
          : 'border-ink-200 bg-white hover:border-cobalt-300 hover:bg-ink-50'
      }`}
    >
      <span
        className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-sm font-semibold transition-colors ${
          selected
            ? 'bg-cobalt-500 text-white'
            : 'bg-ink-100 text-ink-600 group-hover:bg-cobalt-100 group-hover:text-cobalt-700'
        }`}
      >
        {selected ? (
          <Check
            className="h-4 w-4"
            aria-hidden="true"
          />
        ) : (
          letter
        )}
      </span>

      <span className="flex-1 text-base font-medium text-ink-800">
        {option.text}
      </span>
    </button>
  );
}