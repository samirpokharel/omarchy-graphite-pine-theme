local active_border_color = { colors = { "rgba(4f8f63ee)", "rgba(244a33ee)" }, angle = 45 }
local inactive_border_color = "rgba(2a302caa)"

hl.config({
  general = {
    col = {
      active_border = active_border_color,
      inactive_border = inactive_border_color,
    },
  },

  group = {
    col = {
      border_active = active_border_color,
      border_inactive = inactive_border_color,
    },
  },
})

-- Graphite Pine cut corners: a straight 45° bevel instead of a curve.
-- rounding_power = 1 turns the corner arc into a diagonal line. The size is
-- set per window rather than through decoration:rounding because the Omarchy
-- shell mirrors decoration:rounding as a Qt radius, which can only draw
-- curves; leaving the global at 0 keeps the bar and panels from rounding.
hl.config({
  decoration = {
    rounding = 0,
    rounding_power = 1,
  },
})

o.window({ class = ".*" }, { rounding = 12 })
-- Popped windows get rounding = 8 from Omarchy's default/hypr/apps/system.lua.
o.window({ tag = "pop" }, { rounding = 12 })
