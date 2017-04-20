'use strict';

angular.module('try', [
    // external
    // 'angularUtils.directives.dirPagination',
    'ngCookies',
    'ngResource',
    'ngRoute',
    // 'ngFileSaver',
    // 'ngSanitize',
    // 'ng-showdown',
    'ui.bootstrap',
    // // internal
    // 'blogDetail',
    // 'blogList',
    // 'confirmClick',
    // 'loginDetail',
    // 'registerDetail',

    //API Service
    'station',
    'family',
    'parameter',
    'export',

    //Internal
    'modelList',
    'parameterDetail',
    'spcStationList',
    'spcStationDetail',
    'spcTesterDetail',
    'tryNav',
]);