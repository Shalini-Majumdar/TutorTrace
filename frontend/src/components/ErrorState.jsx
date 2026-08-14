import {
  AlertTriangle,
  RefreshCw
} from 'lucide-react';


function getErrorMessage(error) {
  if (!error) {
    return 'Something went wrong.';
  }

  /*
   * Normal JS Error:
   *
   * new Error("Something failed")
   */
  if (
    typeof error === 'object' &&
    typeof error.message === 'string'
  ) {

    /*
     * Sometimes API wrappers throw JSON
     * as a string, e.g.
     *
     * {"detail":"Student not found"}
     *
     * Try to extract FastAPI's detail.
     */
    try {
      const parsed =
        JSON.parse(
          error.message
        );

      if (
        parsed &&
        typeof parsed.detail === 'string'
      ) {
        return parsed.detail;
      }

    } catch {
      // Not JSON. Use the message normally.
    }

    return error.message;
  }


  /*
   * FastAPI-style error object:
   *
   * {
   *   detail: "..."
   * }
   */
  if (
    typeof error === 'object' &&
    typeof error.detail === 'string'
  ) {
    return error.detail;
  }


  /*
   * Pydantic validation errors can return:
   *
   * detail: [...]
   */
  if (
    typeof error === 'object' &&
    Array.isArray(
      error.detail
    )
  ) {

    const firstError =
      error.detail[0];

    if (
      firstError &&
      typeof firstError.msg === 'string'
    ) {
      return firstError.msg;
    }

    return 'The request contains invalid data.';
  }


  /*
   * Plain string error.
   */
  if (
    typeof error === 'string'
  ) {
    return error;
  }


  return 'Something went wrong.';
}


export default function ErrorState({
  error,
  onRetry,
  retryLabel = 'Try again',
  compact = false
}) {

  const isDev =
    import.meta.env.DEV;

  const message =
    getErrorMessage(
      error
    );


  return (
    <div
      className={`flex items-start gap-3 rounded-xl border border-coral-200 bg-coral-50 ${
        compact
          ? 'p-3'
          : 'p-4'
      }`}
      role="alert"
    >

      <AlertTriangle
        className="mt-0.5 h-5 w-5 shrink-0 text-coral-600"
        aria-hidden="true"
      />


      <div className="min-w-0 flex-1">

        <p className="text-sm font-medium text-coral-800">
          {message}
        </p>


        {isDev &&
          error &&
          typeof error === 'object' && (

          <details className="mt-2">

            <summary className="cursor-pointer text-xs font-medium text-coral-600">
              Technical details
            </summary>

            <pre className="mt-2 max-h-40 overflow-auto whitespace-pre-wrap break-words rounded-lg bg-white/60 p-2 text-xs text-coral-700">

              {JSON.stringify(
                error,
                null,
                2
              )}

            </pre>

          </details>

        )}


        {onRetry && (

          <button
            type="button"
            onClick={
              onRetry
            }
            className="mt-3 inline-flex items-center gap-1.5 rounded-lg bg-coral-600 px-3 py-1.5 text-xs font-semibold text-white transition-colors hover:bg-coral-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-coral-400"
          >

            <RefreshCw
              className="h-3.5 w-3.5"
              aria-hidden="true"
            />

            {retryLabel}

          </button>

        )}

      </div>

    </div>
  );
}