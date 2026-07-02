import type { ImageRecord } from "@/lib/rafiki-data";
import { cn } from "@/lib/utils";

interface Props {
  image: ImageRecord;
  className?: string;
  showLabel?: boolean;
}

export function Thumbnail({ image, className, showLabel = true }: Props) {
  if (image.status === "failed") {
    return (
      <div
        className={cn(
          "grid place-items-center bg-black border border-dashed border-destructive/40 text-destructive/70 text-[10px] font-mono uppercase tracking-widest",
          className,
        )}
      >
        Render error
      </div>
    );
  }
  if (image.status === "missing") {
    return (
      <div
        className={cn(
          "grid place-items-center bg-black border border-dashed border-border text-muted-foreground text-[10px] font-mono uppercase tracking-widest",
          className,
        )}
      >
        File missing
      </div>
    );
  }
  return (
    <div
      className={cn(
        "group grid place-items-center relative overflow-hidden outline-1 -outline-offset-1 outline-white/5 transition-[outline-color,transform] duration-200 hover:outline-white/20",
        className,
      )}
      style={{
        background: `linear-gradient(135deg, ${image.swatch} 0%, #0c0c0c 140%)`,
      }}
    >
      <img
        src={image.thumbnailUrl || image.url}
        alt={image.name}
        className="absolute inset-0 h-full w-full object-cover"
        loading="lazy"
      />
      <span className="absolute inset-0 bg-black/10" aria-hidden />
      {/* Subtle sheen on hover */}
      <span
        aria-hidden
        className="pointer-events-none absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
        style={{
          background:
            "linear-gradient(120deg, transparent 30%, rgba(255,255,255,0.06) 50%, transparent 70%)",
        }}
      />
      {showLabel && (
        <span className="relative text-[10px] font-mono uppercase tracking-widest text-white/70 bg-black/45 px-1.5 py-0.5 rounded">
          #{image.slot.toString().padStart(4, "0")}
        </span>
      )}
    </div>
  );
}
