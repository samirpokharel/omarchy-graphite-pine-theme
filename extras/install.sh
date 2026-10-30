#!/bin/bash

# Graphite Pine extras: cut (45° bevel) corners on windows, the Omarchy menu
# and notifications.
#
# A theme installed with `omarchy theme install` can't do this by itself:
# Omarchy drops a repo theme's .lua files and themes can't touch shell
# plugins. This script makes the same changes on request, and undoes them.
#
# Usage: extras/install.sh            apply
#        extras/install.sh --remove   undo
#
# What it changes:
#   - menu and notifications: clones the built-in plugin with
#     `omarchy plugin clone` (or reuses your existing clone), adds
#     ChamferSurface.qml and swaps BorderSurface for it in two/one places.
#     Cloning from your installed Omarchy keeps the rest of the plugin current.
#   - windows: adds a fenced block to ~/.config/hypr/looknfeel.lua, unless the
#     theme's own hyprland.lua already applies (a theme you own, not a clone).

set -euo pipefail

here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
theme_dir="$HOME/.config/omarchy/themes/graphite-pine"
plugins_dir="$HOME/.config/omarchy/plugins"
user="${USER:-$(id -un)}"
looknfeel="$HOME/.config/hypr/looknfeel.lua"
fence_begin="-- >>> graphite-pine corners >>>"
fence_end="-- <<< graphite-pine corners <<<"
marker=".graphite-pine-clone"

say() { printf '  %s\n' "$*"; }

# Omarchy only stages a theme's hyprland.lua when the theme is yours: a plain
# folder or a symlink. A real directory with .git is a repo install.
theme_lua_applies() {
  [[ -L $theme_dir || ! -d $theme_dir/.git ]]
}

# --- plugins ---------------------------------------------------------------

clone_dir() { echo "$plugins_dir/$user.$1"; }

ensure_clone() {
  local name=$1 dir
  dir=$(clone_dir "$name")
  if [[ -d $dir ]]; then
    local from
    from=$(jq -r '.omarchy.clonedFrom // empty' "$dir/manifest.json" 2>/dev/null || true)
    [[ $from == "omarchy.$name" ]] || { say "$dir isn't a clone of omarchy.$name, skipping"; return 1; }
  else
    omarchy plugin clone "omarchy.$name" >/dev/null
    touch "$dir/$marker"
  fi
}

# perl -0 slurps the file so one pattern can span the type name and its id line.
patch_menu() {
  local dir file
  dir=$(clone_dir menu)
  file="$dir/Menu.qml"
  cp "$here/shell/ChamferSurface.qml" "$dir/"
  perl -0pi -e 's/^(\s*)BorderSurface \{\n(\s*)id: card\n/$1ChamferSurface {\n$2id: card\n$2cut: 12\n/m;
                s/delegate: BorderSurface \{\n(\s*)id: row\n/delegate: ChamferSurface {\n$1id: row\n$1cut: 6\n/' "$file"
  grep -q 'ChamferSurface {' "$file" && say "menu: cut corners" || say "menu: Menu.qml layout changed, not patched"
}

patch_notifications() {
  local dir file
  dir=$(clone_dir notifications)
  file="$dir/components/NotificationCard.qml"
  cp "$here/shell/ChamferSurface.qml" "$dir/components/"
  perl -0pi -e 's/^BorderSurface \{\n(\s*)id: root\n/ChamferSurface {\n$1id: root\n$1cut: 12\n/m' "$file"
  grep -q 'ChamferSurface {' "$file" && say "notifications: cut corners" || say "notifications: NotificationCard.qml layout changed, not patched"
}

unpatch() {
  local name=$1 dir
  dir=$(clone_dir "$name")
  [[ -d $dir ]] || return 0
  if [[ -f $dir/$marker ]]; then
    omarchy plugin remove "$user.$name" --yes >/dev/null
    say "$name: removed the clone, built-in restored"
    return
  fi
  # Your own clone: put BorderSurface back and leave everything else alone.
  find "$dir" -name '*.qml' -exec perl -0pi -e 's/ChamferSurface \{\n(\s*)id: (card|row|root)\n\s*cut: \d+\n/BorderSurface {\n$1id: $2\n/g' {} +
  find "$dir" -name ChamferSurface.qml -delete
  say "$name: back to BorderSurface"
}

# --- hyprland --------------------------------------------------------------

add_hypr_block() {
  if theme_lua_applies; then
    say "windows: the theme's hyprland.lua already applies"
    return
  fi
  remove_hypr_block quiet
  { echo; echo "$fence_begin"; cat "$here/hypr-corners.lua"; echo "$fence_end"; } >>"$looknfeel"
  say "windows: cut corners added to $looknfeel"
}

remove_hypr_block() {
  [[ -f $looknfeel ]] && grep -qF -- "$fence_begin" "$looknfeel" || return 0
  perl -0pi -e "s/\n?\Q$fence_begin\E.*?\Q$fence_end\E\n?//s" "$looknfeel"
  [[ ${1:-} == quiet ]] || say "windows: removed the block from $looknfeel"
}

# --- main ------------------------------------------------------------------

if [[ ${1:-} == --remove ]]; then
  echo "Removing Graphite Pine cut corners"
  unpatch menu
  unpatch notifications
  remove_hypr_block
else
  echo "Applying Graphite Pine cut corners"
  ensure_clone menu && patch_menu
  ensure_clone notifications && patch_notifications
  add_hypr_block
fi

hyprctl reload >/dev/null
# The menu and notifications stay loaded, so a file reload isn't enough.
omarchy restart shell >/dev/null 2>&1 || true
echo "Done."
