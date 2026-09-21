type IconProps = { size?: number };

export function SendIcon({ size = 18 }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M22 2 11 13" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M22 2 15 22l-4-9-9-4 20-7Z" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function ChartIcon({ size = 18 }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M3 3v18h18" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M18 17V9M13 17V5M8 17v-4" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function CloseIcon({ size = 18 }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M18 6 6 18M6 6l12 12" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function ChevronIcon({ size = 12 }: IconProps) {
  return (
    <svg className="chevron" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
      <path d="m9 18 6-6-6-6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function ThumbsUpIcon({ size = 15 }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path
        d="M7 22V11l5-9 1.5 1.5c.4.4.5.9.4 1.4L13 9h6a2 2 0 0 1 2 2.3l-1.3 8A3 3 0 0 1 16.8 22H7Z"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path d="M7 11H3v11h4" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function ThumbsDownIcon({ size = 15 }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path
        d="M17 2v11l-5 9-1.5-1.5c-.4-.4-.5-.9-.4-1.4L11 15H5a2 2 0 0 1-2-2.3l1.3-8A3 3 0 0 1 7.2 2H17Z"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path d="M17 13h4V2h-4" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function ManualIcon({ size = 48 }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path
        d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2Z"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path d="M9 7h7M9 11h7" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
