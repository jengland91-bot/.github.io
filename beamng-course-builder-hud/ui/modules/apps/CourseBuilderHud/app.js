angular.module('beamng.apps')
.directive('courseBuilderHud', [function () {
  return {
    templateUrl: '/ui/modules/apps/CourseBuilderHud/app.html',
    replace: true,
    restrict: 'EA',
    scope: true,
    controller: ['$scope', function ($scope) {
      $scope.catalog = []
      $scope.filtered = []
      $scope.placed = []
      $scope.categories = []
      $scope.selectedPropId = null
      $scope.selectedPlacedId = null
      $scope.category = 'course'
      $scope.mode = 'place'
      $scope.yaw = 0
      $scope.scale = 1
      $scope.snap = 15
      $scope.nudge = 0.5
      $scope.count = 0
      $scope.saveName = 'course'
      $scope.saves = []
      $scope.query = ''
      $scope.paintMode = false
      $scope.paintHeld = false
      $scope.paintSpacing = 3
      $scope.gridSnap = false
      $scope.gridSize = 1
      $scope.ghostEnabled = true
      $scope.randomYaw = false
      $scope.randomScale = false

      function lua(cmd) {
        bngApi.engineLua(cmd)
      }

      function filterCatalog() {
        var q = ($scope.query || '').toLowerCase()
        $scope.filtered = ($scope.catalog || []).filter(function (p) {
          if ($scope.category === 'favs') {
            if (!p.favorite) return false
          } else if ($scope.category && p.category !== $scope.category) {
            return false
          }
          if (!q) return true
          return (p.label || '').toLowerCase().indexOf(q) !== -1
        })
      }

      $scope.$on('CourseBuilderHudState', function (_, state) {
        if (!state) return
        $scope.catalog = state.catalog || []
        $scope.placed = state.placed || []
        $scope.categories = state.categories || $scope.categories
        $scope.selectedPropId = state.selectedPropId
        $scope.selectedPlacedId = state.selectedPlacedId
        $scope.yaw = state.yaw
        $scope.scale = state.scale
        $scope.snap = state.snap
        $scope.nudge = state.nudge
        $scope.count = state.count
        $scope.mode = state.mode
        $scope.category = state.category
        $scope.paintMode = !!state.paintMode
        $scope.paintHeld = !!state.paintHeld
        $scope.paintSpacing = state.paintSpacing
        $scope.gridSnap = !!state.gridSnap
        $scope.gridSize = state.gridSize
        $scope.ghostEnabled = !!state.ghostEnabled
        $scope.randomYaw = !!state.randomYaw
        $scope.randomScale = !!state.randomScale
        filterCatalog()
        $scope.$digest()
      })

      $scope.$on('CourseBuilderHudSaves', function (_, names) {
        $scope.saves = names || []
        $scope.$digest()
      })

      $scope.setCategory = function (id) {
        $scope.category = id
        lua('extensions.courseBuilderHud.setCategory("' + id + '")')
        filterCatalog()
      }

      $scope.onSearch = function () { filterCatalog() }

      $scope.selectProp = function (id) {
        $scope.selectedPropId = id
        lua('extensions.courseBuilderHud.selectProp("' + id + '")')
      }

      $scope.toggleFavorite = function (id, $event) {
        if ($event) $event.stopPropagation()
        lua('extensions.courseBuilderHud.toggleFavorite("' + id + '")')
      }

      $scope.selectPlaced = function (id) {
        lua('extensions.courseBuilderHud.selectPlaced(' + id + ')')
      }

      $scope.place = function () { lua('extensions.courseBuilderHud.place()') }
      $scope.undo = function () { lua('extensions.courseBuilderHud.undo()') }
      $scope.clear = function () { lua('extensions.courseBuilderHud.clear()') }
      $scope.scan = function () { lua('extensions.courseBuilderHud.scan()') }

      $scope.rotateLeft = function () {
        lua('extensions.courseBuilderHud.rotate(-' + ($scope.snap || 15) + ')')
      }
      $scope.rotateRight = function () {
        lua('extensions.courseBuilderHud.rotate(' + ($scope.snap || 15) + ')')
      }
      $scope.setSnap = function (snap) {
        lua('extensions.courseBuilderHud.setSnap(' + snap + ')')
      }

      $scope.nudgeRel = function (f, r, u) {
        var s = $scope.nudge || 0.5
        lua('extensions.courseBuilderHud.nudgeRel(' + (f * s) + ',' + (r * s) + ',' + (u * s) + ')')
      }

      $scope.setScale = function (v) {
        lua('extensions.courseBuilderHud.setScale(' + v + ')')
      }
      $scope.bumpScale = function (d) {
        var next = Math.max(0.1, Math.round((($scope.scale || 1) + d) * 10) / 10)
        $scope.setScale(next)
      }

      $scope.togglePaint = function () {
        lua('extensions.courseBuilderHud.togglePaintMode()')
      }
      $scope.setPaintSpacing = function (v) {
        lua('extensions.courseBuilderHud.setPaintSpacing(' + v + ')')
      }
      $scope.bumpPaintSpacing = function (d) {
        var next = Math.max(0.5, Math.round((($scope.paintSpacing || 3) + d) * 10) / 10)
        $scope.paintSpacing = next
        $scope.setPaintSpacing(next)
      }

      $scope.toggleGrid = function () {
        lua('extensions.courseBuilderHud.toggleGridSnap()')
      }
      $scope.setGridSize = function (v) {
        lua('extensions.courseBuilderHud.setGridSize(' + v + ')')
      }
      $scope.bumpGrid = function (d) {
        var next = Math.max(0.25, Math.round((($scope.gridSize || 1) + d) * 100) / 100)
        $scope.gridSize = next
        $scope.setGridSize(next)
      }

      $scope.toggleGhost = function () {
        lua('extensions.courseBuilderHud.toggleGhost()')
      }
      $scope.toggleRandomYaw = function () {
        lua('extensions.courseBuilderHud.toggleRandomYaw()')
      }
      $scope.toggleRandomScale = function () {
        lua('extensions.courseBuilderHud.toggleRandomScale()')
      }

      $scope.deleteSelected = function () { lua('extensions.courseBuilderHud.deleteSelected()') }
      $scope.duplicateSelected = function () { lua('extensions.courseBuilderHud.duplicateSelected()') }
      $scope.reaimSelected = function () { lua('extensions.courseBuilderHud.reaimSelected()') }

      $scope.save = function () {
        var name = ($scope.saveName || 'course').replace(/[^a-zA-Z0-9\-_]/g, '_')
        lua('extensions.courseBuilderHud.save("' + name + '")')
        lua('extensions.courseBuilderHud.listSaves()')
      }
      $scope.load = function (name) {
        var n = name || $scope.saveName || 'course'
        lua('extensions.courseBuilderHud.load("' + n + '")')
      }
      $scope.exportPrefab = function () {
        var name = ($scope.saveName || 'course').replace(/[^a-zA-Z0-9\-_]/g, '_')
        lua('extensions.courseBuilderHud.exportPrefab("' + name + '")')
      }

      lua('extensions.courseBuilderHud.refresh()')
      lua('extensions.courseBuilderHud.listSaves()')
    }]
  }
}])
