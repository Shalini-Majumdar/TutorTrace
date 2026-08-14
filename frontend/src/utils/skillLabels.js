export const SKILL_LABELS = {
  integer_operations: 'Integer Operations',
  fraction_operations: 'Fraction Operations',
  order_of_operations: 'Order of Operations',
  distributive_property: 'Distributive Property',
  one_step_equations: 'One-Step Equations',
  two_step_equations: 'Two-Step Equations',
  inequalities: 'Inequalities',
  exponents: 'Exponents',
};

export const SKILL_ORDER = [
  'integer_operations',
  'fraction_operations',
  'order_of_operations',
  'distributive_property',
  'one_step_equations',
  'two_step_equations',
  'inequalities',
  'exponents',
];

export function skillLabel(skillId) {
  return SKILL_LABELS[skillId] || formatLabel(skillId);
}

export function formatLabel(value) {
  if (!value) return '';
  return value
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

export const MISCONCEPTION_EXPLANATIONS = {
  sign_error: 'You may be mixing up positive and negative signs.',
  inverse_operation_error: 'You may be applying the inverse operation incorrectly.',
  coefficient_isolation_error: 'You may need to isolate the variable coefficient before solving.',
  negative_distribution_error: 'Watch how the negative value distributes across every term.',
  absolute_value_confusion: 'Double-check the sign when combining values of different magnitude.',
  larger_magnitude_sign_error: 'When adding signed numbers, the sign follows the larger magnitude.',
  common_denominator_error: 'Check how you created the common denominator.',
};

export function misconceptionExplanation(key) {
  return MISCONCEPTION_EXPLANATIONS[key] || formatLabel(key);
}

export const SELECTION_REASON_COPY = {
  cold_start_coverage: 'Building your starting skill profile.',
  prerequisite_diagnosis: 'A weaker prerequisite may be blocking progress.',
  active_prerequisite_diagnosis: 'Checking a foundational skill before continuing.',
  misconception_investigation: 'Checking whether a repeated error pattern is present.',
  weakest_mastery: 'Practicing your current weakest skill.',
  epsilon_exploration: 'Mixing in another skill to keep your learner model calibrated.',
  fallback_unused_question: 'Continuing with an unseen question.',
};

export function selectionReasonCopy(type) {
  return SELECTION_REASON_COPY[type] || formatLabel(type);
}
