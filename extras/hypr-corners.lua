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
