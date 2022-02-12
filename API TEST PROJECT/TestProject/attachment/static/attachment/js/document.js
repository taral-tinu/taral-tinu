function documentInit() {
    var documents = {};
    $('#loading-image').hide();
    sparrow.registerCtrl(
        'documentditCtrl',
        function ($scope, $rootScope, $route, $routeParams, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, $interpolate, ModalService, $compile) {
            $scope.addViewButtons('');
            var detailPageEditMode = false;
            var tagAutoLookupConfig = {
                iframeData: {
                    url: '#/attachment/tag/0',
                    title: 'Add tag',
                },
                addLooupItemTitle: 'Add tag',
            };
            setAutoLookup('id_tag', '/b/lookups/document_tag/', '', false, false, false, null, 10, null, null, tagAutoLookupConfig);
            var config = {
                pageTitle: 'Document',
            };
            $scope.saveDocument = function () {
                var postData = {
                    id: $routeParams.id,
                };
                sparrow.postForm(postData, $('#frmdocument'), $scope, switchEditMode);
            };
            function switchEditMode(data) {
                if (data.id != undefined && data.id != '') {
                    window.location.hash = '#/document/edit/' + data.id + '/';
                    $route.reload();
                }
            }

            $scope.onClose = function (e) {
                if (detailPageEditMode) {
                    $route.reload();
                    return;
                }
                if (sparrow.inIframe()) {
                    if (parent.globalIndex.iframeCloseCallback.length > 0) {
                        var iFrameCloseCallback = parent.globalIndex.iframeCloseCallback.pop();
                        iFrameCloseCallback('', orderData);
                    }
                } else {
                    $scope.goBack(e, '');
                }
            };
            if ($routeParams.id != 0) {
                sparrow.applyReadOnlyMode('#frmdocument');
            }

            $scope.applyEditMode = function (e) {
                detailPageEditMode = true;
                sparrow.applyEditMode('#frmdocument', '#id_title');
            };
            sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config, ModalService);
        }
    );

    return documents;
}

documentInit();
