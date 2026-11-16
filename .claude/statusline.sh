#!/usr/bin/env bash
# Barre de statut Claude Code : utilisation de la session sous la barre de prompt.
input=$(cat)
j() { echo "$input" | jq -r "$1 // empty" 2>/dev/null; }

model=$(j '.model.display_name')
ctx=$(j '.context_window.used_percentage')
five=$(j '.rate_limits.five_hour.used_percentage')
five_reset=$(j '.rate_limits.five_hour.resets_at')
week=$(j '.rate_limits.seven_day.used_percentage')
cost=$(j '.cost.total_cost_usd')
dur=$(j '.cost.total_duration_ms')

GREEN=$'\e[32m'; YELLOW=$'\e[33m'; RED=$'\e[31m'; DIM=$'\e[2m'; RESET=$'\e[0m'

# Barre de progression colorée : bar <pourcentage>
bar() {
  local p=${1%.*}
  p=${p:-0}
  if (( p > 100 )); then p=100; fi
  local filled=$(( p / 10 )) color=$GREEN out="" i
  if (( p >= 50 )); then color=$YELLOW; fi
  if (( p >= 80 )); then color=$RED; fi
  for (( i = 0; i < 10; i++ )); do
    if (( i < filled )); then out+="█"; else out+="░"; fi
  done
  printf "%s%s %d%%%s" "$color" "$out" "$p" "$RESET"
}

parts=()
[ -n "$model" ] && parts+=("🤖 $model")
if [ -n "$five" ]; then
  s="⏱ Session $(bar "$five")"
  if [ -n "$five_reset" ]; then
    left=$(( (${five_reset%.*} - $(date +%s)) / 60 ))
    if (( left > 0 )); then
      s+=" ${DIM}(reset $((left / 60))h$(printf %02d $((left % 60))))${RESET}"
    fi
  fi
  parts+=("$s")
fi
[ -n "$week" ] && parts+=("📅 Semaine $(bar "$week")")
[ -n "$ctx" ] && parts+=("🧠 Contexte $(bar "$ctx")")
[ -n "$cost" ] && parts+=("💰 \$$(printf %.2f "$cost")")
[ -n "$dur" ] && parts+=("⌛ $(( ${dur%.*} / 60000 ))min")

out=""
for p in "${parts[@]}"; do
  [ -n "$out" ] && out+=" ${DIM}│${RESET} "
  out+="$p"
done
printf "%s" "$out"
