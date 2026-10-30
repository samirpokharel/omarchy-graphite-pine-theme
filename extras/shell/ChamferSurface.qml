import QtQuick
import QtQuick.Shapes
import qs.Commons

// Drop-in for qs.Ui BorderSurface with cut corners: each corner is a straight
// 45° bevel instead of an arc, matching Hyprland windows drawn with
// rounding_power = 1. Same borderSpec/padding/contentInset API, so the menu
// code only swaps the type name. `cut` is the bevel length along each edge.
Item {
  id: root

  property color color: "transparent"
  property real cut: 12
  property real radius: 0 // accepted for BorderSurface compatibility; unused

  property var borderSpec: Border.none()
  property real padding: 0
  property real topPadding: padding
  property real rightPadding: padding
  property real bottomPadding: padding
  property real leftPadding: padding

  readonly property real borderTop: Border.top(borderSpec)
  readonly property real borderRight: Border.right(borderSpec)
  readonly property real borderBottom: Border.bottom(borderSpec)
  readonly property real borderLeft: Border.left(borderSpec)
  readonly property real contentTopInset: borderTop + topPadding
  readonly property real contentRightInset: borderRight + rightPadding
  readonly property real contentBottomInset: borderBottom + bottomPadding
  readonly property real contentLeftInset: borderLeft + leftPadding

  readonly property real _c: Math.max(0, Math.min(cut, width / 2, height / 2))
  readonly property bool _hasBorder: Math.max(borderTop, borderRight, borderBottom, borderLeft) > 0
  readonly property var _gradient: borderSpec && borderSpec.gradient ? borderSpec.gradient : ({ colors: [], angle: 0, enabled: false })
  readonly property var _colors: _gradient.enabled ? _gradient.colors : [Border.color(borderSpec)]
  readonly property var _ends: endpoints(width, height, _gradient.angle || 0)

  // Octagon with corners cut by c, inset by per-side widths. Keeping the
  // diagonal parallel and exactly w away from the outer one shortens the
  // inner cut by w·(2 − √2) for a uniform border.
  function octagon(x0, y0, x1, y1, c) {
    c = Math.max(0, Math.min(c, (x1 - x0) / 2, (y1 - y0) / 2))
    return "M " + (x0 + c) + " " + y0 + " L " + (x1 - c) + " " + y0 + " L " + x1 + " " + (y0 + c)
      + " L " + x1 + " " + (y1 - c) + " L " + (x1 - c) + " " + y1 + " L " + (x0 + c) + " " + y1
      + " L " + x0 + " " + (y1 - c) + " L " + x0 + " " + (y0 + c) + " Z"
  }

  function innerCut() {
    var w = Math.max(borderTop, borderRight, borderBottom, borderLeft)
    return Math.max(0, _c - w * (2 - Math.SQRT2))
  }

  // Same CSS-style endpoints as BorderGeometry.gradientEndpoints.
  function endpoints(w, h, angle) {
    w = Math.max(1, w); h = Math.max(1, h)
    var rad = angle * Math.PI / 180, dx = Math.cos(rad), dy = Math.sin(rad)
    var len = (Math.abs(w * dx) + Math.abs(h * dy)) / 2
    return { x1: w / 2 - dx * len, y1: h / 2 - dy * len, x2: w / 2 + dx * len, y2: h / 2 + dy * len }
  }

  function stopColor(i) { return _colors.length ? _colors[Math.min(i, _colors.length - 1)] : "transparent" }
  function stopPos(i) { return _colors.length <= 1 ? (i === 0 ? 0 : 1) : Math.min(1, i / (_colors.length - 1)) }

  Shape {
    anchors.fill: parent
    z: -1
    visible: root.color.a > 0 && root.width > 0 && root.height > 0
    preferredRendererType: Shape.CurveRenderer
    ShapePath {
      strokeWidth: 0
      strokeColor: "transparent"
      fillColor: root.color
      PathSvg { path: root.octagon(0, 0, root.width, root.height, root._c) }
    }
  }

  Shape {
    anchors.fill: parent
    z: 100000
    visible: root._hasBorder && root.width > 0 && root.height > 0
    preferredRendererType: Shape.CurveRenderer
    ShapePath {
      strokeWidth: 0
      strokeColor: "transparent"
      fillRule: ShapePath.OddEvenFill
      fillGradient: LinearGradient {
        x1: root._ends.x1; y1: root._ends.y1
        x2: root._ends.x2; y2: root._ends.y2
        GradientStop { position: root.stopPos(0); color: root.stopColor(0) }
        GradientStop { position: root.stopPos(1); color: root.stopColor(1) }
        GradientStop { position: root.stopPos(2); color: root.stopColor(2) }
        GradientStop { position: root.stopPos(3); color: root.stopColor(3) }
      }
      PathSvg {
        path: root.octagon(0, 0, root.width, root.height, root._c) + " "
          + root.octagon(root.borderLeft, root.borderTop, root.width - root.borderRight, root.height - root.borderBottom, root.innerCut())
      }
    }
  }
}
