export default function Logo({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden
    >
      <rect
        width="32"
        height="32"
        rx="8"
        fill="var(--primary)"
        fillOpacity="0.12"
      />
      <path
        d="M10 10h10v2H10v-2zm0 5h10v2H10v-2zm0 5h6v2h-6v-2z"
        fill="var(--primary)"
      />
      <path
        d="M22 16l3 3-3 3"
        stroke="var(--primary)"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
