const LEVELS = [
  {
    key: 'low',
    label: 'Low',
    value: 0.25
  },
  {
    key: 'medium',
    label: 'Medium',
    value: 0.5
  },
  {
    key: 'high',
    label: 'High',
    value: 0.85
  },
];


export default function ConfidenceSelector({
  value,
  onChange,
  disabled
}) {
  return (
    <div className="flex flex-col gap-2">

      <span className="text-xs font-semibold uppercase tracking-wide text-ink-400">
        Confidence

        <span className="font-normal normal-case text-ink-300">
          {' '}
          (optional)
        </span>
      </span>


      <div className="inline-flex w-full max-w-xs rounded-lg border border-ink-200 bg-ink-50 p-0.5">

        {LEVELS.map((level) => {

          const active =
            value === level.value;

          return (
            <button
              key={level.key}
              type="button"
              onClick={() =>
                onChange(
                  active
                    ? null
                    : level.value
                )
              }
              disabled={disabled}
              aria-pressed={active}
              className={`flex flex-1 items-center justify-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-semibold transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-cobalt-400 disabled:opacity-50 ${
                active
                  ? 'bg-white text-cobalt-700 shadow-sm'
                  : 'text-ink-500 hover:text-ink-700'
              }`}
            >
              {level.label}
            </button>
          );
        })}

      </div>

    </div>
  );
}