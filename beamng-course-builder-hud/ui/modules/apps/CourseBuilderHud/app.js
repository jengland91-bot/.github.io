angular.module('beamng.apps')
.directive('courseBuilderHud', [function () {
  return {
    templateUrl: '/ui/modules/apps/CourseBuilderHud/app.html',
    replace: true,
    restrict: 'EA',
    scope: true,
    controller: ['$scope', function ($scope) {
      $scope.catalog = []
      $scope.placed = []
      $scope.selectedPropId = null
      $scope.yaw = 0
      $scope.snap = 15
      $scope.count = 0
      $scope.saveName = 'course'
      $scope.saves = []
      $scope.status = 'Ready — look where you want it, then Place'

      function lua(cmd) {
        bngApi.engineLua(cmd)
      }

      $scope.$on('CourseBuilderHudState', function (_, state) {
        if (!state) return
        $scope.catalog = state.catalog || $scope.catalog
        $scope.placed = state.placed || []
        $scope.selectedPropId = state.selectedPropId
        $scope.yaw = state.yaw
        $scope.snap = state.snap
        $scope.count = state.count
        $scope.$digest()
      })

      $scope.$on('CourseBuilderHudSaves', function (_, names) {
        $scope.saves = names || []
        $scope.$digest()
      })

      $scope.selectProp = function (id) {
        $scope.selectedPropId = id
        lua('extensions.courseBuilderHud.selectProp("' + id + '")')
      }

      $scope.place = function () {
        $scope.status = 'Placing…'
        lua('extensions.courseBuilderHud.place()')
      }

      $scope.undo = function () {
        lua('extensions.courseBuilderHud.undo()')
      }

      $scope.clear = function () {
        lua('extensions.courseBuilderHud.clear()')
      }

      $scope.rotateLeft = function () {
        lua('extensions.courseBuilderHud.rotate(-' + ($scope.snap || 15) + ')')
      }

      $scope.rotateRight = function () {
        lua('extensions.courseBuilderHud.rotate(' + ($scope.snap || 15) + ')')
      }

      $scope.setSnap = function (snap) {
        lua('extensions.courseBuilderHud.setSnap(' + snap + ')')
      }

      $scope.save = function () {
        var name = ($scope.saveName || 'course').replace(/[^a-zA-Z0-9\-_]/g, '_')
        lua('extensions.courseBuilderHud.save("' + name + '")')
        lua('extensions.courseBuilderHud.listSaves()')
      }

      $scope.load = function (name) {
        var n = name || $scope.saveName || 'course'
        lua('extensions.courseBuilderHud.load("' + n + '")')
      }

      $scope.refreshSaves = function () {
        lua('extensions.courseBuilderHud.listSaves()')
      }

      // Pull initial state once the app mounts
      lua('extensions.courseBuilderHud.refresh()')
      lua('extensions.courseBuilderHud.listSaves()')
    }]
  }
}])
