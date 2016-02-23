(function(){
    "use strict";

    var app = angular.module('app', ['ngMaterial']);
	
	app.controller('formController', ['$scope', '$http', '$mdDialog', function($scope,$http, $mdDialog) {
		$scope.formData = {};

		$scope.midiin = 0;
		$scope.midiout = 0;
		$scope.osc = 0;
		$scope.completeMsg = "";

		$scope.alert = $mdDialog.alert({ title: 'Please wait',
				content: 'Rebooting PiLink....', ok: "WAIT"});


		$scope.refreshLogs = function() {
			$http.get('logs').then(function(resp) {
				$scope.midiin = resp.data.activity.midiin
				$scope.midiout = resp.data.activity.midiout
				$scope.osc = resp.data.activity.oscin
				$scope.completeMsg = resp.data.messages.join("\n")
			}, function (resp) {
				console.log(resp)
				$scope.midiin = -1
				$scope.midiout = -1
				$scope.osc = -1
				$scope.completeMsg = "!!! UNABLE TO GET PILINK LOGS !!!"
			})
		}

		$scope.rebootDevice = function() {
			$http.get('reboot')
			setTimeout(function() { location.reload() } , 5000);
			$mdDialog.show( $scope.alert ).finally(function() { location.reload() } )
		}


		$scope.processForm = function() {
			$http.post('config', $scope.formData).then(function(resp) {
				$scope.rebootDevice()		
			}, function(resp) {
				console.log(resp)
				alert("ERROR: Something went wrong with the PiLink config update.")
			})
		};

		$http.get('config').then(function(resp) {
			$scope.formData = resp.data;
			$scope.mididev_lst = resp.data['mididev_lst']
		}, function(resp) {
			console.log(resp)
		});

		$scope.refreshLogs()
	}]);
	
})();

/*
	// this is kept so the log(completeMsg) can contain html

	angular.module('app').filter('to_trusted', ['$sce', function($sce) {
	    return function(text) {
	        return $sce.trustAsHtml(text);
	    };
	<div ng-bind-html="completeMsg | to_trusted"></div>        
	}]);

*/

