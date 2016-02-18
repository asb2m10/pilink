(function(){
    "use strict";

    var app = angular.module('app', ['ngMaterial']);
	app.controller('formController', ['$scope', '$http', function($scope,$http) {

		// create a blank object to hold our form information
		// $scope will allow this to pass between controller and view
		$scope.formData = {};

		$http({ method : 'GET', url : 'config' }).success(function(data) {
			$scope.formData = data;
			console.log(data)
		});

		$scope.processForm = function() {
			$http({
		        method  : 'POST',
		        url     : 'config',
		        data    : $scope.formData,
		    }).success(function(data) {
		        if (!data.success) {
		            //$scope.errorName = data.errors.name;
		        } else {
                    //$scope.errorName = '';
		        }
		    });
		};
			
	}]);

})();

