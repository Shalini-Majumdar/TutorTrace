import {
  useCallback,
  useRef,
  useState
} from 'react';

import {
  Brain,
  GraduationCap,
  LogIn
} from 'lucide-react';

import * as api from '@/api/tutorTraceApi';

import {
  SKILL_ORDER,
  skillLabel
} from '@/utils/skillLabels';

import {
  masteryBand,
  toPercentage
} from '@/utils/formatters';

import QuestionCard from '@/components/QuestionCard';
import AnswerFeedback from '@/components/AnswerFeedback';
import SelectionReason from '@/components/SelectionReason';
import MasteryOverview from '@/components/MasteryOverview';
import DiagnosticPanel from '@/components/DiagnosticPanel';
import ErrorState from '@/components/ErrorState';
import Skeleton from '@/components/Skeleton';


/* =========================================================
   SESSION START
   ========================================================= */

function SessionStart({
  onStart,
  starting,
  error
}) {
  const [
    studentId,
    setStudentId
  ] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();

    const cleanId =
      studentId.trim();

    if (
      cleanId &&
      !starting
    ) {
      onStart(cleanId);
    }
  };

  return (
    <div className="mx-auto flex max-w-xl flex-col items-center px-4 py-16">
      <div className="mb-6 flex h-14 w-14 items-center justify-center rounded-2xl bg-cobalt-600 text-white shadow-card">
        <Brain
          className="h-7 w-7"
          aria-hidden="true"
        />
      </div>

      <h1 className="text-center font-serif text-3xl font-medium text-ink-900">
        TutorTrace
      </h1>

      <p className="mt-1 text-center text-sm font-medium uppercase tracking-wide text-cobalt-600">
        Adaptive Math Session
      </p>

      <form
        onSubmit={handleSubmit}
        className="mt-8 w-full"
      >
        <label
          htmlFor="student-id"
          className="mb-1.5 block text-sm font-medium text-ink-600"
        >
          Student ID
        </label>

        <input
          id="student-id"
          type="text"
          value={studentId}
          onChange={(e) =>
            setStudentId(
              e.target.value
            )
          }
          placeholder="e.g. student-42"
          autoFocus
          className="w-full rounded-xl border border-ink-200 bg-white px-4 py-3 text-base text-ink-900 placeholder:text-ink-300 focus:border-cobalt-400 focus:outline-none focus:ring-2 focus:ring-cobalt-200"
        />

        <button
          type="submit"
          disabled={
            !studentId.trim() ||
            starting
          }
          className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-cobalt-600 px-5 py-3 text-base font-semibold text-white transition-colors hover:bg-cobalt-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-cobalt-400 focus-visible:ring-offset-1 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <LogIn
            className="h-5 w-5"
            aria-hidden="true"
          />

          {starting
            ? 'Starting…'
            : 'Start Learning'}
        </button>
      </form>

      <p className="mt-5 text-center text-sm text-ink-400">
        Your session adapts to mastery,
        response patterns, and prerequisite gaps.
      </p>

      {error && (
        <div className="mt-6 w-full">
          <ErrorState
            error={error}
            onRetry={() =>
              onStart(
                studentId.trim()
              )
            }
            retryLabel="Restart session"
          />
        </div>
      )}
    </div>
  );
}


/* =========================================================
   MASTERY DISPLAY CONFIG
   ========================================================= */

const BAND_DOT = {
  coral: 'bg-coral-500',
  amber: 'bg-amber-500',
  teal: 'bg-teal-500',
  sage: 'bg-sage-500',
  ink: 'bg-ink-300'
};


const BAND_TEXT = {
  coral: 'text-coral-600',
  amber: 'text-amber-600',
  teal: 'text-teal-600',
  sage: 'text-sage-600',
  ink: 'text-ink-500'
};


/* =========================================================
   CONTEXT RAIL
   ========================================================= */

function ContextRail({
  question,
  selectionReason,
  mastery,
  diagnostics
}) {
  const currentSkill =
    question?.skill_id;

  /*
   * IMPORTANT:
   *
   * Backend mastery shape:
   *
   * skills: {
   *   integer_operations: {...},
   *   fraction_operations: {...}
   * }
   *
   * It is NOT an array.
   *
   * Therefore use dictionary lookup,
   * not .find().
   */
  const skillMastery =
    currentSkill
      ? mastery?.skills?.[
          currentSkill
        ]
      : null;

  const band =
    masteryBand(
      skillMastery
        ?.effective_mastery
    );

  return (
    <aside className="space-y-5">

      {/* CURRENT SKILL */}
      <div>
        <h3 className="mb-2 text-sm font-semibold text-ink-800">
          Current skill
        </h3>

        {skillMastery ? (
          <div className="rounded-xl border border-ink-200 bg-white p-3.5">

            <div className="flex items-center justify-between">

              <span className="text-sm font-medium text-ink-700">
                {skillLabel(
                  currentSkill
                )}
              </span>

              <span
                className={`text-sm font-bold tabular-nums ${
                  BAND_TEXT[
                    band.color
                  ] ||
                  'text-ink-500'
                }`}
              >
                {toPercentage(
                  skillMastery
                    .effective_mastery
                )}
                %
              </span>

            </div>

            <div className="mt-2 flex items-center gap-2">

              <span
                className={`h-2 w-2 rounded-full ${
                  BAND_DOT[
                    band.color
                  ] ||
                  'bg-ink-300'
                }`}
              />

              <span className="text-xs text-ink-400">
                {band.label}
              </span>

            </div>
          </div>
        ) : (
          <div className="rounded-xl border border-ink-200 bg-ink-50 p-3.5">
            <p className="text-sm text-ink-400">
              Assessing…
            </p>
          </div>
        )}
      </div>


      {/* WHY THIS QUESTION */}
      {selectionReason && (
        <SelectionReason
          reason={
            selectionReason
          }
          skillId={
            currentSkill
          }
        />
      )}


      {/* DIAGNOSTICS */}
      {diagnostics && (
        <DiagnosticPanel
          diagnostics={
            diagnostics
          }
        />
      )}


      {/* ALL SKILLS */}
      {mastery && (
        <div className="border-t border-ink-100 pt-4">
          <MasteryOverview
            mastery={mastery}
            skillOrder={
              SKILL_ORDER
            }
            activeSkillId={
              currentSkill
            }
          />
        </div>
      )}

    </aside>
  );
}


/* =========================================================
   STUDENT SESSION
   ========================================================= */

export default function StudentSession() {

  const [
    studentId,
    setStudentId
  ] = useState(null);

  /*
   * start
   * loading
   * question
   * submitting
   * feedback
   * continuing
   */
  const [
    phase,
    setPhase
  ] = useState('start');


  /*
   * IMPORTANT:
   *
   * Store the actual question only.
   *
   * Backend next-question response:
   *
   * {
   *   question: {...},
   *   selection_reason: {...}
   * }
   */
  const [
    question,
    setQuestion
  ] = useState(null);


  const [
    selectionReason,
    setSelectionReason
  ] = useState(null);


  const [
    feedback,
    setFeedback
  ] = useState(null);


  const [
    mastery,
    setMastery
  ] = useState(null);


  const [
    diagnostics,
    setDiagnostics
  ] = useState(null);


  const [
    error,
    setError
  ] = useState(null);


  const [
    selectedOptionId,
    setSelectedOptionId
  ] = useState(null);


  const [
    confidence,
    setConfidence
  ] = useState(null);


  const questionStartRef =
    useRef(null);


  /* =======================================================
     LOAD MASTERY + DIAGNOSTICS
     ======================================================= */

  const loadMasteryAndDiagnostics =
    useCallback(
      async (id) => {

        try {

          const [
            masteryResponse,
            diagnosticResponse
          ] = await Promise.all([
            api.getMastery(id),
            api.getDiagnostics(id)
          ]);

          setMastery(
            masteryResponse
          );

          setDiagnostics(
            diagnosticResponse
          );

        } catch (err) {

          /*
           * These are supplementary panels.
           * Failure should not block answering.
           */
          console.error(
            'Could not load mastery/diagnostics:',
            err
          );
        }

      },
      []
    );


  /* =======================================================
     LOAD NEXT QUESTION
     ======================================================= */

  const loadNextQuestion =
    useCallback(
      async (id) => {

        const response =
          await api.getNextQuestion(
            id
          );

        /*
         * Correct backend shape:
         *
         * response.question
         * response.selection_reason
         */
        setQuestion(
          response.question
        );

        setSelectionReason(
          response.selection_reason
        );

        setSelectedOptionId(
          null
        );

        setConfidence(
          null
        );

        setFeedback(
          null
        );

        /*
         * Start response timer only
         * once new question is rendered.
         */
        questionStartRef.current =
          performance.now();

        return response;

      },
      []
    );


  /* =======================================================
     START SESSION
     ======================================================= */

  const startSession =
    useCallback(
      async (id) => {

        setError(null);
        setPhase('loading');

        try {

          await api.startStudent(
            id
          );

          setStudentId(
            id
          );

          await loadNextQuestion(
            id
          );

          setPhase(
            'question'
          );

          loadMasteryAndDiagnostics(
            id
          );

        } catch (err) {

          console.error(
            'Failed to start TutorTrace session:',
            err
          );

          setError(
            err
          );

          setPhase(
            'start'
          );
        }

      },
      [
        loadMasteryAndDiagnostics,
        loadNextQuestion
      ]
    );


  /* =======================================================
     SUBMIT ANSWER
     ======================================================= */

  const handleSubmit =
    useCallback(
      async (
        isDontKnow = false
      ) => {

        if (
          !studentId ||
          !question
        ) {
          return;
        }

        /*
         * Normal selected answers
         * require an option.
         */
        if (
          !isDontKnow &&
          selectedOptionId == null
        ) {
          return;
        }


        setError(null);
        setPhase('submitting');


        /*
         * Actual elapsed response time.
         */
        const timeTaken =
          questionStartRef.current
            ? (
                performance.now()
                -
                questionStartRef.current
              ) / 1000
            : 0;


        /*
         * IMPORTANT:
         *
         * Backend expects:
         *
         * question_id
         * answer_type
         * time_taken_seconds
         *
         * selected_option_id only for
         * selected_option answers.
         */
        const payload = {
          question_id:
            question.id,

          answer_type:
            isDontKnow
              ? 'dont_know'
              : 'selected_option',

          time_taken_seconds:
            Math.round(
              timeTaken * 100
            ) / 100
        };


        /*
         * Add selected option ONLY
         * for normal answers.
         */
        if (!isDontKnow) {

          payload.selected_option_id =
            selectedOptionId;

        }


        /*
         * Confidence is optional.
         */
        if (
          confidence != null
        ) {

          payload.confidence =
            confidence;

        }


        try {

          const result =
            await api.submitAnswer(
              studentId,
              payload
            );


          setFeedback(
            result
          );


          setPhase(
            'feedback'
          );


          /*
           * Refresh rail after BKT state
           * has changed.
           */
          loadMasteryAndDiagnostics(
            studentId
          );

        } catch (err) {

          console.error(
            'Answer submission failed:',
            err
          );

          setError(
            err
          );

          setPhase(
            'question'
          );
        }

      },
      [
        studentId,
        question,
        selectedOptionId,
        confidence,
        loadMasteryAndDiagnostics
      ]
    );


  /* =======================================================
     CONTINUE
     ======================================================= */

  const handleContinue =
    useCallback(
      async () => {

        if (!studentId) {
          return;
        }

        setError(null);
        setPhase('continuing');

        try {

          await loadNextQuestion(
            studentId
          );

          setPhase(
            'question'
          );

          loadMasteryAndDiagnostics(
            studentId
          );

        } catch (err) {

          console.error(
            'Failed to load next question:',
            err
          );

          setError(
            err
          );

          /*
           * Keep feedback visible so the
           * learner can retry Continue.
           */
          setPhase(
            'feedback'
          );
        }

      },
      [
        studentId,
        loadNextQuestion,
        loadMasteryAndDiagnostics
      ]
    );


  /* =======================================================
     RESTART LOCAL SESSION VIEW
     ======================================================= */

  const handleRestart =
    useCallback(
      () => {

        setStudentId(null);
        setPhase('start');

        setQuestion(null);
        setSelectionReason(null);

        setFeedback(null);
        setMastery(null);
        setDiagnostics(null);
        setError(null);

        setSelectedOptionId(null);
        setConfidence(null);

        questionStartRef.current =
          null;

      },
      []
    );


  /* =======================================================
     START SCREEN
     ======================================================= */

  if (
    phase === 'start'
  ) {

    return (
      <SessionStart
        onStart={
          startSession
        }
        starting={
          false
        }
        error={
          error
        }
      />
    );
  }


  /* =======================================================
     INITIAL LOADING
     ======================================================= */

  if (
    phase === 'loading'
  ) {

    return (
      <div className="mx-auto max-w-5xl px-4 py-10">

        <div className="grid gap-6 lg:grid-cols-[1fr_340px]">

          <div className="space-y-4">

            <Skeleton className="h-6 w-32" />
            <Skeleton className="h-10 w-3/4" />

            <Skeleton className="h-14 w-full" />
            <Skeleton className="h-14 w-full" />
            <Skeleton className="h-14 w-full" />

          </div>

          <div className="space-y-4">

            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-32 w-full" />

          </div>

        </div>

      </div>
    );
  }


  /*
   * Keep feedback visible while the
   * next question is loading.
   */
  const showResult =
    phase === 'feedback' ||
    phase === 'continuing';


  /* =======================================================
     MAIN SESSION UI
     ======================================================= */

  return (
    <div className="mx-auto max-w-6xl px-4 py-6">

      {/* SESSION HEADER */}
      <div className="mb-5 flex items-center justify-between">

        <div className="flex items-center gap-2.5">

          <GraduationCap
            className="h-5 w-5 text-cobalt-600"
            aria-hidden="true"
          />

          <span className="text-sm font-medium text-ink-500">
            Session
          </span>

          <span className="text-sm font-semibold text-ink-800">
            {studentId}
          </span>

        </div>


        <button
          type="button"
          onClick={
            handleRestart
          }
          className="rounded-lg px-3 py-1.5 text-xs font-medium text-ink-400 transition-colors hover:bg-ink-100 hover:text-ink-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-ink-300"
        >
          Restart session
        </button>

      </div>


      {/* ERROR */}
      {error && (
        <div className="mb-5">

          <ErrorState
            error={
              error
            }
            onRetry={
              showResult
                ? handleContinue
                : () =>
                    loadMasteryAndDiagnostics(
                      studentId
                    )
            }
            retryLabel="Retry"
          />

        </div>
      )}


      {/* MAIN GRID */}
      <div className="grid gap-6 lg:grid-cols-[1fr_340px]">

        {/* QUESTION / FEEDBACK */}
        <div className="min-w-0">

          {showResult ? (

            <AnswerFeedback
              feedback={
                feedback
              }
              onContinue={
                handleContinue
              }
              continuing={
                phase ===
                'continuing'
              }
            />

          ) : (

            <div className="animate-fade-in rounded-2xl border border-ink-200 bg-white p-6 shadow-card">

              <QuestionCard
                question={
                  question
                }
                selectedOptionId={
                  selectedOptionId
                }
                onSelectOption={
                  setSelectedOptionId
                }
                confidence={
                  confidence
                }
                onConfidenceChange={
                  setConfidence
                }
                onSubmit={() =>
                  handleSubmit(false)
                }
                onDontKnow={() =>
                  handleSubmit(true)
                }
                submitting={
                  phase ===
                  'submitting'
                }
                showResult={
                  false
                }
              />

            </div>
          )}


          {/* ORIGINAL QUESTION DURING FEEDBACK */}
          {showResult &&
            question && (

            <div className="mt-4 rounded-2xl border border-ink-200 bg-white/60 p-4 opacity-70">

              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-ink-400">
                Question
              </p>

              <p className="font-serif text-lg text-ink-700">
                {
                  question.prompt
                }
              </p>

            </div>

          )}

        </div>


        {/* CONTEXT */}
        <ContextRail
          question={
            question
          }
          selectionReason={
            selectionReason
          }
          mastery={
            mastery
          }
          diagnostics={
            diagnostics
          }
        />

      </div>

    </div>
  );
}