import {
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  Clock,
  GitBranch,
  HelpCircle,
  TrendingDown,
  TrendingUp,
  XCircle,
} from 'lucide-react';

import {
  misconceptionExplanation,
  skillLabel
} from '@/utils/skillLabels';

import {
  toPercentage
} from '@/utils/formatters';

import MasteryBar from './MasteryBar';


/* =========================================================
   RESPONSE SIGNAL COPY
   ========================================================= */

function SignalCopy({ signal }) {
  if (!signal) {
    return null;
  }

  const copy = {
    slow_correct:
      'Correct — this one took a little more effort.',

    speed_slip:
      'Check your work — this may have been a quick slip.',

    explicit_uncertainty:
      "That's okay. TutorTrace will use that uncertainty to adapt what comes next.",
  };

  const text =
    copy[signal];

  if (!text) {
    return null;
  }

  return (
    <p className="text-sm text-ink-600">
      <Clock
        className="mr-1.5 inline h-3.5 w-3.5 text-ink-400"
        aria-hidden="true"
      />

      {text}
    </p>
  );
}


/* =========================================================
   ANSWER FEEDBACK
   ========================================================= */

export default function AnswerFeedback({
  feedback,
  onContinue,
  continuing
}) {
  if (!feedback) {
    return null;
  }


  /*
   * IMPORTANT:
   *
   * These names MUST match the FastAPI
   * submit-answer response.
   *
   * Backend returns:
   *
   * correct
   * mastery_before
   * mastery_after
   * uncertainty_detected
   */
  const isCorrect =
    feedback.correct === true;

  const isIncorrect =
    feedback.correct === false;

  const isUncertain =
    feedback.uncertainty_detected === true ||
    feedback.response_signal ===
      'explicit_uncertainty';


  const prevMastery =
    feedback.mastery_before;

  const newMastery =
    feedback.mastery_after;


  const masteryDelta =
    prevMastery != null &&
    newMastery != null
      ? newMastery -
        prevMastery
      : null;


  /* =======================================================
     HEADER
     ======================================================= */

  let headerIcon;
  let headerText;
  let headerColor;


  if (isUncertain) {

    headerIcon = (
      <HelpCircle
        className="h-5 w-5 text-amber-600"
        aria-hidden="true"
      />
    );

    headerText =
      'Uncertainty acknowledged';

    headerColor =
      'amber';

  } else if (isCorrect) {

    headerIcon = (
      <CheckCircle2
        className="h-5 w-5 text-sage-600"
        aria-hidden="true"
      />
    );

    headerText =
      'Correct';

    headerColor =
      'sage';

  } else if (isIncorrect) {

    headerIcon = (
      <XCircle
        className="h-5 w-5 text-coral-600"
        aria-hidden="true"
      />
    );

    headerText =
      'Not quite';

    headerColor =
      'coral';

  } else {

    /*
     * Defensive fallback.
     * Should rarely happen.
     */
    headerIcon = (
      <HelpCircle
        className="h-5 w-5 text-ink-500"
        aria-hidden="true"
      />
    );

    headerText =
      'Response recorded';

    headerColor =
      'amber';
  }


  const headerStyles = {
    sage:
      'border-sage-200 bg-sage-50',

    coral:
      'border-coral-200 bg-coral-50',

    amber:
      'border-amber-200 bg-amber-50',
  };


  return (
    <div
      className={`animate-slide-up space-y-4 rounded-2xl border-2 p-5 ${
        headerStyles[
          headerColor
        ]
      }`}
      role="status"
      aria-live="polite"
    >

      {/* ===================================================
          HEADER
          =================================================== */}

      <div className="-m-5 mb-1 flex items-center gap-2.5 rounded-t-2xl border-b-2 border-inherit p-5">

        {headerIcon}

        <h3 className="text-lg font-semibold text-ink-900">
          {headerText}
        </h3>

      </div>


      <div className="space-y-4 px-1 pb-1">


        {/* =================================================
            MASTERY CHANGE
            ================================================= */}

        {prevMastery != null &&
          newMastery != null && (

          <div className="rounded-xl border border-ink-200 bg-white p-4">

            <div className="mb-2 flex items-center justify-between">

              <span className="text-xs font-semibold uppercase tracking-wide text-ink-400">
                Mastery
              </span>


              <div className="flex items-center gap-1.5 text-sm font-semibold tabular-nums">

                <span className="text-ink-400">
                  {toPercentage(
                    prevMastery
                  )}
                  %
                </span>


                <ArrowRight
                  className="h-4 w-4 text-ink-300"
                  aria-hidden="true"
                />


                <span className="text-ink-900">
                  {toPercentage(
                    newMastery
                  )}
                  %
                </span>


                {masteryDelta >
                  0.001 && (

                  <span className="ml-1 inline-flex items-center gap-0.5 text-xs text-sage-600">

                    <TrendingUp className="h-3.5 w-3.5" />

                    +
                    {toPercentage(
                      masteryDelta
                    )}

                  </span>
                )}


                {masteryDelta <
                  -0.001 && (

                  <span className="ml-1 inline-flex items-center gap-0.5 text-xs text-coral-600">

                    <TrendingDown className="h-3.5 w-3.5" />

                    {toPercentage(
                      masteryDelta
                    )}

                  </span>
                )}

              </div>

            </div>


            <MasteryBar
              value={
                newMastery
              }
              showLabel={
                false
              }
              animate
            />

          </div>

        )}


        {/* =================================================
            RESPONSE SIGNAL
            ================================================= */}

        <SignalCopy
          signal={
            feedback.response_signal
          }
        />


        {/* =================================================
            MISCONCEPTION
            ================================================= */}

        {feedback
          .misconception_detected &&
          feedback
            .misconception && (

          <div className="flex items-start gap-2.5 rounded-xl border border-amber-200 bg-amber-50/60 p-3.5">

            <AlertTriangle
              className="mt-0.5 h-4 w-4 shrink-0 text-amber-600"
              aria-hidden="true"
            />


            <div>

              <p className="text-sm font-semibold text-amber-800">
                Pattern noticed
              </p>


              <p className="mt-0.5 text-sm text-ink-700">

                {misconceptionExplanation(
                  feedback
                    .misconception
                )}

              </p>

            </div>

          </div>

        )}


        {/* =================================================
            PREREQUISITE PIVOT
            ================================================= */}

        {feedback
          .diagnostic_pivot_triggered &&
          feedback
            .diagnostic_pivot && (

          <div className="rounded-xl border-2 border-cobalt-200 bg-cobalt-50/70 p-4">

            <div className="flex items-center gap-2">

              <GitBranch
                className="h-4 w-4 text-cobalt-600"
                aria-hidden="true"
              />

              <span className="text-xs font-semibold uppercase tracking-wide text-cobalt-700">
                Checking a prerequisite
              </span>

            </div>


            <p className="mt-2 text-sm text-ink-700">

              {skillLabel(
                feedback
                  .diagnostic_pivot
                  .target_skill_id
              )}

              {' '}
              may be blocked by{' '}

              <span className="font-medium text-ink-900">

                {skillLabel(
                  feedback
                    .diagnostic_pivot
                    .pivot_skill_id
                )}

              </span>

              . TutorTrace will briefly
              check that foundation
              before returning.

            </p>

          </div>

        )}


        {/* =================================================
            CONTINUE
            ================================================= */}

        <button
          type="button"
          onClick={
            onContinue
          }
          disabled={
            continuing
          }
          className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-ink-900 px-5 py-3 text-sm font-semibold text-white transition-colors hover:bg-ink-800 focus:outline-none focus-visible:ring-2 focus-visible:ring-ink-400 focus-visible:ring-offset-1 disabled:opacity-60 sm:w-auto"
        >

          {continuing
            ? 'Loading next question…'
            : 'Continue'}

          {!continuing && (
            <ArrowRight
              className="h-4 w-4"
              aria-hidden="true"
            />
          )}

        </button>

      </div>

    </div>
  );
}