import { HelpCircle, Send } from 'lucide-react';

import AnswerOption from './AnswerOption';
import ConfidenceSelector from './ConfidenceSelector';

import { difficultyLabel } from '@/utils/formatters';
import { skillLabel } from '@/utils/skillLabels';


export default function QuestionCard({
  question,
  selectedOptionId,
  onSelectOption,
  confidence,
  onConfidenceChange,
  onSubmit,
  onDontKnow,
  submitting,
  showResult = false,
}) {
  if (!question) {
    return null;
  }

  const options =
    Array.isArray(question.options)
      ? question.options
      : [];

  const canSubmit =
    selectedOptionId != null &&
    !submitting &&
    !showResult;


  return (
    <article className="space-y-5">

      <div className="flex flex-wrap items-center gap-2 text-xs">

        <span className="rounded-md bg-cobalt-100 px-2.5 py-1 font-semibold text-cobalt-700">
          {skillLabel(question.skill_id)}
        </span>

        <span className="rounded-md bg-ink-100 px-2.5 py-1 font-medium text-ink-600">
          {difficultyLabel(question.difficulty)}
        </span>

      </div>


      <div>
        <h2 className="font-serif text-2xl font-medium leading-snug text-ink-900">
          {question.prompt}
        </h2>
      </div>


      <div
        className="space-y-2.5"
        role="group"
        aria-label="Answer options"
      >

        {options.map((option, index) => (

          <AnswerOption
            key={option.id}
            option={option}
            index={index}
            selected={
              selectedOptionId === option.id
            }
            onSelect={onSelectOption}
            disabled={
              submitting ||
              showResult
            }
          />

        ))}

      </div>


      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">

        <ConfidenceSelector
          value={confidence}
          onChange={onConfidenceChange}
          disabled={
            submitting ||
            showResult
          }
        />


        <div className="flex items-center gap-2.5">

          <button
            type="button"
            onClick={onDontKnow}
            disabled={
              submitting ||
              showResult
            }
            className="inline-flex items-center gap-1.5 rounded-lg border border-ink-200 bg-white px-4 py-2.5 text-sm font-medium text-ink-600 transition-colors hover:border-ink-300 hover:bg-ink-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-ink-300 disabled:opacity-50"
          >

            <HelpCircle
              className="h-4 w-4"
              aria-hidden="true"
            />

            I don't know

          </button>


          <button
            type="button"
            onClick={onSubmit}
            disabled={!canSubmit}
            className="inline-flex items-center gap-1.5 rounded-lg bg-cobalt-600 px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-cobalt-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-cobalt-400 focus-visible:ring-offset-1 disabled:cursor-not-allowed disabled:opacity-40"
          >

            <Send
              className="h-4 w-4"
              aria-hidden="true"
            />

            {submitting
              ? 'Checking…'
              : 'Submit'}

          </button>

        </div>

      </div>

    </article>
  );
}