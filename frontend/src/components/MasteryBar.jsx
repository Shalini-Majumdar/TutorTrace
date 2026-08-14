import {
  useEffect,
  useRef,
  useState
} from 'react';

import {
  masteryBand,
  toPercentage
} from '@/utils/formatters';


const BAND_COLORS = {
  coral: {
    bar: 'bg-coral-500',
    track: 'bg-coral-100',
    text: 'text-coral-700',
    dot: 'bg-coral-500'
  },

  amber: {
    bar: 'bg-amber-500',
    track: 'bg-amber-100',
    text: 'text-amber-700',
    dot: 'bg-amber-500'
  },

  teal: {
    bar: 'bg-teal-500',
    track: 'bg-teal-100',
    text: 'text-teal-700',
    dot: 'bg-teal-500'
  },

  sage: {
    bar: 'bg-sage-500',
    track: 'bg-sage-100',
    text: 'text-sage-700',
    dot: 'bg-sage-500'
  },

  ink: {
    bar: 'bg-ink-400',
    track: 'bg-ink-100',
    text: 'text-ink-500',
    dot: 'bg-ink-400'
  }
};


export default function MasteryBar({
  value,
  label,
  showLabel = true,
  animate = true,
  size = 'md'
}) {
  /*
   * Backend mastery values should always be
   * probabilities in the range 0..1.
   *
   * Clamp defensively so temporary frontend
   * state cannot break the visual.
   */
  const safeValue =
    typeof value === 'number'
      ? Math.min(
          1,
          Math.max(
            0,
            value
          )
        )
      : 0;


  const targetPct =
    toPercentage(
      safeValue
    );


  const [
    displayPct,
    setDisplayPct
  ] = useState(
    animate
      ? 0
      : targetPct
  );


  const prevRef =
    useRef(
      animate
        ? 0
        : targetPct
    );


  useEffect(() => {

    if (!animate) {

      setDisplayPct(
        targetPct
      );

      prevRef.current =
        targetPct;

      return;
    }


    const start =
      prevRef.current;

    const end =
      targetPct;


    if (
      start === end
    ) {
      return;
    }


    const duration =
      600;

    const startTime =
      performance.now();

    let raf;


    const tick = (now) => {

      const elapsed =
        now - startTime;

      const t =
        Math.min(
          elapsed / duration,
          1
        );


      const eased =
        1 -
        Math.pow(
          1 - t,
          3
        );


      setDisplayPct(
        Math.round(
          start +
          (
            end - start
          ) *
          eased
        )
      );


      if (
        t < 1
      ) {

        raf =
          requestAnimationFrame(
            tick
          );

      } else {

        prevRef.current =
          end;

      }
    };


    raf =
      requestAnimationFrame(
        tick
      );


    return () => {

      if (raf) {
        cancelAnimationFrame(
          raf
        );
      }

    };

  }, [
    targetPct,
    animate
  ]);


  const band =
    masteryBand(
      safeValue
    );


  const colors =
    BAND_COLORS[
      band.color
    ] ||
    BAND_COLORS.ink;


  const heightClass =
    size === 'sm'
      ? 'h-1.5'
      : 'h-2';


  return (
    <div className="w-full">

      {showLabel && (

        <div className="mb-1 flex items-center justify-between">

          <span className="text-xs font-medium text-ink-500">
            {label || band.label}
          </span>

          <span
            className={`text-xs font-semibold tabular-nums ${
              colors.text
            }`}
          >
            {displayPct}%
          </span>

        </div>

      )}


      <div
        className={`w-full overflow-hidden rounded-full ${
          colors.track
        } ${
          heightClass
        }`}
      >

        <div
          className={`h-full rounded-full ${
            colors.bar
          } transition-[width] duration-100 ease-out`}
          style={{
            width:
              `${displayPct}%`
          }}
        />

      </div>

    </div>
  );
}