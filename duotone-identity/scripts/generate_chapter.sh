#!/bin/bash
# generate_chapter.sh - Scaffold new chapter section

chapter_num="$1"

if [ -z "$chapter_num" ]; then
  echo "Usage: generate_chapter.sh <chapter-number>"
  exit 1
fi

# Determine if light or dark (odd = light, even = dark)
if [ $((chapter_num % 2)) -eq 1 ]; then
  isLight="true"
  bg_color="var(--cream)"
  text_color="var(--charcoal)"
  svg_fill="#141413"
  svg_stroke="#141413"
else
  isLight="false"
  bg_color="var(--charcoal)"
  text_color="var(--cream)"
  svg_fill="#FAF9F5"
  svg_stroke="#FAF9F5"
fi

cat <<EOF
{/* Chapter $chapter_num */}
<ChapterSection
  number={$chapter_num}
  label="Chapter Label"
  description={{
    title: "Chapter Title",
    paragraphs: [
      "First paragraph describing the chapter content.",
      "Second paragraph with more details."
    ]
  }}
  isLight={$isLight}
>
  <div className="illustration">
    <svg viewBox="0 0 500 500" className="w-full h-full">
      <!-- Your SVG paths here -->
      <!-- Use .fill-path for shapes, .draw-path for lines -->

      <circle className="fill-path" cx="250" cy="250" r="50"
              fill="$svg_fill" opacity="0"/>
    </svg>
  </div>
</ChapterSection>
EOF
