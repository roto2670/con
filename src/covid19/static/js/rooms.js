const UPLOAD_URL_BUILDERS = {
        INTERNAL: _.template('https://172.16.5.8:10443/api/upload/master/update'),
        EXTERNAL: _.template('https://skec-fujairah.loc8.dev:10443/api/upload/master/update')
    },
    DOWNLOAD_URL_BUILDERS = {
        INTERNAL: _.template('https://172.16.5.8:10443/api/download/<%= type %>/<%= id %>'),
        EXTERNAL: _.template('https://skec-fujairah.loc8.dev:10443/api/download/<%= type %>/<%= id %>')
    },
    UPLOAD_URL_BUILDER = window.IS_INTERNAL ? UPLOAD_URL_BUILDERS.INTERNAL : UPLOAD_URL_BUILDERS.EXTERNAL,
    DOWNLOAD_URL_BUILDER = window.IS_INTERNAL ? DOWNLOAD_URL_BUILDERS.INTERNAL : DOWNLOAD_URL_BUILDERS.EXTERNAL;
const LICENSE_KEY =
    'CompanyName=Kith Creative Inc.,LicensedApplication=SCS,LicenseType=SingleApplication,LicensedConcurrentDeveloperCount=1,LicensedProductionInstancesCount=0,AssetReference=AG-015479,ExpiryDate=9_May_2022_[v2]_MTY1MjA1MDgwMDAwMA==94d947d25667951aa892d1334d29ff9b';
const PAGE_SIZE = 15,
    CACHE_KEY = {
        ROOMS: '_r_grid_sts_'
    };

let _db = firebase.firestore(),
    _roomsGridOptions = null,
    _usersGridOptions = null;

let _loadingData = false,
    _lastSnapShot = null,
    _currentUser = null,
    _selectedFilters = [];

let _roomTransactions = {
    add: [], // TODO: not implemented
    remove: [], // TODO: not implemented
    update: []
};

start();

async function start() {
    _showLoading();

    _initHandlers();
    _initGrid();
    _initRoomsGrid();
    _initUsersGrid();

    await _displayRooms(null, true);
    _hideLoading();

    // TODO;
    // _displayUser('999-0000-0000000-5');
}

function stop() {
    // nothing yet.
}

async function _displayRooms(filters, clean) {
    if (!!clean) {
        _clearRoomsGrid();
    }

    if (!_loadingData) {
        _loadingData = true;
        _selectedFilters = filters;

        const _result = await _loadRooms(_lastSnapShot, filters);
        if (!!_result.lastSnapShot) {
            _lastSnapShot = _result.lastSnapShot;
        }

        // render rooms.
        if (!_.isEmpty(_result.dataList)) {
            _addRoomItems(_result.dataList);
        }

        _loadingData = false;
    } else {
        console.debug('Already loading rooms.');
    }
}

async function _displayRoomsByUser(user) {
    if (!user) {
        return;
    }

    // Make selected filter
    _selectedFilters = {
        foods: {
            op: '',
            value: ''
        }
    };
}

async function _displayUser(userId) {
    _clearUsersGrid();

    const _userList = await _loadUsers([userId]);
    _addUserItem(_.first(_userList));
}

function _addRoomItems(dataList) {
    _roomsGridOptions.api.applyTransaction({
        add: dataList
    });
}

function _addUserItem(user) {
    _usersGridOptions.api.applyTransaction({
        add: [user]
    });
}

function _getRoomData(id) {
    return _roomsGridOptions.api.getRowNode(id)?.data;
}

function _getSelectedUsers() {
    return _usersGridOptions.api.getSelectedNodes().map((node) => node.data);
}

function _getSelectedUserIdList() {
    return _.map(_getSelectedUsers(), (user) => user.documentId);
}

async function _assignUsers(roomData, userIdList) {
    if (roomData && !_.isEmpty(userIdList)) {
        const _update = _.clone(roomData);
        _update.dwellers = _.uniq([].concat(roomData.dwellers, _.compact(userIdList)));
        _update.occupancy = _.size(_update.dwellers);

        // check fully
        if (roomData.capacity < _.size(_update.dwellers)) {
            new PNotify({
                type: 'error',
                text: `The ${roomData.documentId} is full.`
            });
            return;
        }

        // apply to grid
        _roomsGridOptions.api.applyTransaction({
            update: [_update]
        });

        _updateRoomsTransaction('update', roomData.documentId, _.compact(userIdList));
        // _db.collection('rooms').doc(roomData.documentId).update({
        //     dwellers: _update.dwellers,
        //     occupancy: _update.occupancy
        // });
    } else {
        console.warn('Failed to assign to room by given room data or user id is empty or null.');
        new PNotify({
            type: 'error',
            text: 'Please select the user first.'
        });
    }
}

function _unAssginUsers(roomData, userIdList) {
    if (roomData && !_.isEmpty(userIdList)) {
        const _update = _.clone(roomData);
        _update.dwellers = _.without(roomData.dwellers, ...userIdList);
        _update.occupancy = _.size(_update.dwellers);

        _roomsGridOptions.api.applyTransaction({
            update: [_update]
        });

        _updateRoomsTransaction('remove', roomData.documentId, _.compact(userIdList));
        // _db.collection('rooms').doc(roomData.documentId).update({
        //     dwellers: _update.dwellers,
        //     occupancy: _update.occupancy
        // });
    } else {
        console.warn('Failed to un-assign to room by given room data or user id is empty or null.');
    }
}

function _saveGridStates(key, columnApi) {
    const _savedState = columnApi.getColumnState();
    localStorage.setItem(key, JSON.stringify(_savedState));

    console.log('Saved grid states.');
}

function _loadGridStates(key, columnApi) {
    try {
        const _savedState = JSON.parse(localStorage.getItem(key));
        if (_savedState) {
            columnApi.applyColumnState({
                state: _savedState,
                applyOrder: true
            });

            console.log('Loaded grid states.');
        }
    } catch (error) {
        // nothing.
        console.warn('Failed to load grid states.', error);
    }
}

function _updateFilters(user) {
    function _update(button, value, defaultName = 'None') {
        if (value) {
            button.removeClass('disabled');
            button.text(value);
        } else {
            button.addClass('disabled');
            button.text(defaultName);
        }
    }

    _update($('.user-filter-btn.categories'), user?.category);
    _update($('.user-filter-btn.departments'), user?.department);
    _update($('.user-filter-btn.foods'), user?.food);
    _update($('.user-filter-btn.nationalities'), user?.nationality);
    _update($('.user-filter-btn.religions'), user?.religion);
}

function _updateRoomsTransaction(key, roomId, userIdList) {
    _roomTransactions[key] = _.reject(_roomTransactions[key], (data) => data.roomId === roomId);
    _roomTransactions[key].push({
        roomId: roomId,
        userIdList: userIdList
    });
}

async function _applyRoomTransactions() {
    console.log('Try apply rooms transactions to db', _roomTransactions);

    const _data = await _toTransaction(_roomTransactions);
    // check appliable first.
    if (_.isEmpty(_data)) {
        new PNotify({
            type: 'error',
            text: `There is no changes.`
        });
        return;
    }

    if (_.size(_roomTransactions.update) >= 1) {
        if (
            window.confirm(
                'It takes a long time to apply the master file. Please apply all changes. Would you still like to proceed?'
            )
        ) {
            $.post(UPLOAD_URL_BUILDER(), _data);
        }
    } else if (window.confirm('Are you sure?')) {
        $.post(UPLOAD_URL_BUILDER(), _data);
    }
    // Refresh data
    _roomTransactions = {
        add: [],
        remove: [],
        update: []
    };
}

async function _toTransaction(transactionDataList) {
    const _result = {};

    // Handle remove first.
    _.each(transactionDataList.remove, (data) => {
        _.each(data.userIdList, (userId) => {
            _result[userId] = { camp: '' };
        });
    });

    _.each(transactionDataList.update, (data) => {
        _.each(data.userIdList, (userId) => {
            _result[userId] = { camp: data.roomId };
        });
    });

    if (!_.isEmpty(_result)) {
        const _currentUser = await _loadCurrentUser();
        _result.admin = _currentUser.documentId;
        return _result;
    }
}

async function _loadRooms(startAt, filters) {
    var query = null;
    query = _db.collection('rooms');
    if (!!startAt) {
        // Paging
        query = query.startAfter(startAt);
    }
    query = query.limit(PAGE_SIZE);

    // Adds filter if has
    if (!!filters) {
        _.each(filters, function (value, key) {
            if (key === 'full') {
                query = query.where(key, '==', !!!value); // TODO
            } else {
                query = query.where(key, 'array-contains', value);
            }
        });
    }
    _selectedFilters = filters;

    // do query
    const _snapshots = await query.get();

    let _resultList = [],
        _lastSnapShot;
    if (!!!_snapshots.empty) {
        _lastSnapShot = _snapshots.docs[_snapshots.docs.length - 1];
        _snapshots.forEach((doc) => {
            let _data = doc.data();
            _data.documentId = doc.id;
            _resultList.push(_data);
        });
    } else {
        // no more rooms.
    }

    return {
        dataList: _resultList,
        lastSnapShot: _lastSnapShot
    };
}

async function _loadUsers(userIdList) {
    return await Promise.all(
        userIdList.map(async (id) => {
            const _doc = await _db.collection('users').doc(id).get();
            const _data = _doc.data();
            _data.documentId = _doc.id;

            return _data;
        })
    );
}

function _clearRoomsGrid() {
    _roomsGridOptions?.api?.setRowData([]);
}

function _clearUsersGrid() {
    _usersGridOptions?.api?.setRowData([]);
}

function _showLoading() {
    $('.rooms-item-loader-btn').addClass('loading');
}

function _hideLoading() {
    $('.rooms-item-loader-btn').removeClass('loading');
}

async function _loadCurrentUser() {
    if (!_currentUser) {
        let _doc = await _db.collection('users').doc(firebase.auth().currentUser.uid).get();
        if (_doc) {
            _currentUser = _doc.data();
            _currentUser.documentId = _doc.id;
        }
    }
    return _currentUser;
}

function _initGrid() {
    // Set license key
    agGrid.LicenseManager.setLicenseKey(LICENSE_KEY);
}

function _initRoomsGrid() {
    // TODO: infinite
    _roomsGridOptions = {
        animateRows: true,
        rowClass: 'room-table-row',
        getRowNodeId: function (data) {
            return data.documentId;
        },
        defaultColDef: {
            flex: 1,
            sortable: false,
            resizable: true,
            editable: false,
            filter: false,
            suppressMenu: true
            // cellStyle: {
            //     height: '100%'
            // }
        },
        onColumnVisible: ({ columnApi }) => {
            _saveGridStates(CACHE_KEY.ROOMS, columnApi);
        },
        onColumnResized: ({ columnApi }) => {
            _saveGridStates(CACHE_KEY.ROOMS, columnApi);
        },
        onColumnMoved: ({ columnApi }) => {
            _saveGridStates(CACHE_KEY.ROOMS, columnApi);
        },
        sideBar: {
            toolPanels: [
                {
                    id: 'columns',
                    labelDefault: 'Columns',
                    labelKey: 'columns',
                    iconKey: 'columns',
                    toolPanel: 'agColumnsToolPanel',
                    toolPanelParams: {
                        suppressRowGroups: true,
                        suppressValues: true,
                        suppressPivots: true,
                        suppressPivotMode: true,
                        suppressSideButtons: true,
                        suppressColumnFilter: true,
                        suppressColumnSelectAll: true,
                        suppressColumnExpandAll: true
                    }
                }
            ]
        },
        autoGroupColumnDef: {
            headerName: 'Camp',
            minWidth: 170
        },
        groupDefaultExpanded: 1,
        columnDefs: [
            {
                headerName: 'Camp',
                field: 'camp',
                flex: 2,
                rowGroup: true,
                hide: true
            },
            {
                headerName: 'Number',
                field: 'number',
                flex: 0,
                width: 80,
                cellRenderer: 'agGroupCellRenderer'
            },
            {
                headerName: 'Group',
                field: 'group'
            },
            {
                headerName: 'Usage',
                field: 'usage'
            },
            {
                headerName: 'Capacity',
                field: 'capacity',
                flex: 0,
                width: 80,
                valueGetter: (params) => {
                    let _left = params.data?.occupancy,
                        _right = params.data?.capacity;
                    if (!_.isNumber(_left)) {
                        _left = 'N/A';
                    }
                    if (!_.isNumber(_right)) {
                        _right = 'N/A';
                    }

                    return `${_left}/${_right}`;
                }
            },
            {
                headerName: 'Religions',
                field: 'religions'
            },
            {
                headerName: 'Genders',
                field: 'genders'
            },
            {
                headerName: 'Nationalities',
                field: 'nationalities'
            },
            {
                headerName: 'Departments',
                field: 'departments'
            },
            {
                headerName: 'Areas',
                field: 'areas'
            },
            {
                headerName: 'Categories',
                field: 'categories'
            },
            {
                headerName: 'Job Category1',
                field: 'job_cats1'
            },
            {
                headerName: 'Job Category2',
                field: 'job_cats2'
            },
            {
                headerName: 'Foods',
                field: 'foods'
            },
            {
                headerName: 'Assign',
                cellRenderer: (params) => {
                    if (params.data) {
                        const _button = $('<div class="btn">Assign</div>');
                        _button.click(() => {
                            _assignUsers(_getRoomData(params.data.documentId), _getSelectedUserIdList());
                        });

                        return _button.get(0);
                    }
                }
            }
        ],
        masterDetail: true,
        detailCellRendererParams: {
            detailGridOptions: {
                animateRows: true,
                rowClass: 'user-table-row',
                getRowNodeId: function (data) {
                    return data.documentId;
                },
                defaultColDef: {
                    flex: 1,
                    sortable: false,
                    resizable: true,
                    editable: false,
                    filter: false,
                    suppressMenu: true,
                    cellStyle: {
                        height: '100%'
                    }
                },
                rowSelection: 'multiple',
                columnDefs: [
                    {
                        headerName: 'Name',
                        flex: 2,
                        minWidth: 200,
                        cellRenderer: function (params) {
                            let data = params.data;
                            let nameCell = $('<div class="user-item-cell name">'),
                                nameContainer = $('<div class="user-item-content-container name">'),
                                profile = $('<div class="user-item-avatar">'),
                                nameLabel = $('<div class="user-item-name-label">'),
                                idLabel = $('<div class="user-item-id-label">');
                            nameCell.append(profile, nameContainer);
                            nameContainer.append(nameLabel, idLabel);

                            // Updates the profile image
                            let profileUrl = DOWNLOAD_URL_BUILDER({
                                type: 'image',
                                id: data.documentId
                            });
                            $('<img/>')
                                .load(function () {
                                    $(cell.getElement())
                                        .find('.user-item-avatar')
                                        .css('background-image', 'url(' + profileUrl + ')');
                                })
                                .attr('src', profileUrl);

                            nameLabel.text(data.fullname);
                            idLabel.text('(' + data.documentId + ')');

                            return nameCell.prop('outerHTML');
                        }
                    },
                    {
                        headerName: 'Gender',
                        field: 'gender'
                    },
                    {
                        headerName: 'Nationality',
                        field: 'nationality'
                    },
                    {
                        headerName: 'Employer',
                        field: 'employer'
                    },
                    {
                        headerName: 'Camp',
                        field: 'camp'
                    },
                    {
                        headerName: 'Room',
                        field: 'room'
                    },
                    {
                        headerName: 'Phone Number',
                        field: 'phone_number'
                    },
                    {
                        headerName: 'Department',
                        field: 'department'
                    },
                    {
                        headerName: 'PV Area',
                        field: 'pv_area'
                    },
                    {
                        headerName: 'Job Category',
                        cellRenderer: (params) => {
                            let _jobCategory1 = params.data.job_cat1 || '',
                                _jobCategory2 = params.data.job_cat2 || '';

                            if (_jobCategory1) {
                                if (_jobCategory2) {
                                    return `${_jobCategory1}/${_jobCategory2}`;
                                }
                                return _jobCategory1;
                            }

                            return _jobCategory2;
                        }
                    },
                    {
                        headerName: 'Unassign',
                        cellRenderer: (params) => {
                            const _button = $('<div class="btn">Unassign</div>');
                            _button.click(() => {
                                _unAssginUsers(_getRoomData(params.data?.roomDocumentId), [params?.data?.documentId]);
                            });

                            return _button.get(0);
                        }
                    }
                ]
            },
            getDetailRowData: async (params) => {
                if (_.isArray(params.data.dwellers)) {
                    const _userList = await _loadUsers(params.data.dwellers);
                    params.successCallback(
                        _.map(_userList, (userData) => {
                            userData.roomDocumentId = params.data.documentId;
                            return userData;
                        })
                    );
                }
            }
        }
    };

    new agGrid.Grid($('.rooms-table').get(0), _roomsGridOptions);
    _loadGridStates(CACHE_KEY.ROOMS, _roomsGridOptions.columnApi);
}

function _initUsersGrid() {
    _usersGridOptions = {
        animateRows: true,
        rowClass: 'user-table-row',
        rowSelection: 'multiple',
        getRowNodeId: function (data) {
            return data.documentId;
        },
        overlayNoRowsTemplate: 'Search for the target person first.',
        defaultColDef: {
            flex: 1,
            sortable: false,
            resizable: true,
            editable: false,
            filter: false,
            suppressMenu: true,
            cellStyle: {
                height: '100%'
            }
        },
        columnDefs: [
            {
                headerName: 'Name',
                flex: 2,
                minWidth: 200,
                checkboxSelection: true,
                cellRenderer: (params) => {
                    let data = params.data;
                    let nameCell = $('<div class="user-item-cell name">'),
                        nameContainer = $('<div class="user-item-content-container name">'),
                        profile = $('<div class="user-item-avatar">'),
                        nameLabel = $('<div class="user-item-name-label">'),
                        idLabel = $('<div class="user-item-id-label">');
                    nameCell.append(profile, nameContainer);
                    nameContainer.append(nameLabel, idLabel);

                    // Updates the profile image
                    let profileUrl = DOWNLOAD_URL_BUILDER({
                        type: 'image',
                        id: data.documentId
                    });
                    $('<img/>')
                        .load(function () {
                            $(cell.getElement())
                                .find('.user-item-avatar')
                                .css('background-image', 'url(' + profileUrl + ')');
                        })
                        .attr('src', profileUrl);

                    nameLabel.text(data.fullname);
                    idLabel.text('(' + data.documentId + ')');

                    return nameCell.prop('outerHTML');
                }
            },
            {
                headerName: 'Gender',
                field: 'gender'
            },
            {
                headerName: 'Nationality',
                field: 'nationality'
            },
            {
                headerName: 'Employer',
                field: 'employer'
            },
            {
                headerName: 'Camp',
                field: 'camp'
            },
            {
                headerName: 'Room',
                field: 'room'
            },
            {
                headerName: 'Phone Number',
                field: 'phone_number'
            },
            {
                headerName: 'Department',
                field: 'department'
            },
            {
                headerName: 'PV Area',
                field: 'pv_area'
            },
            {
                headerName: 'Job Category',
                cellRenderer: (params) => {
                    let _jobCategory1 = params.data.job_cat1 || '',
                        _jobCategory2 = params.data.job_cat2 || '';

                    if (_jobCategory1) {
                        if (_jobCategory2) {
                            return `${_jobCategory1}/${_jobCategory2}`;
                        }
                        return _jobCategory1;
                    }

                    return _jobCategory2;
                }
            }
        ],
        onRowSelected: ({ node, data }) => {
            if (node.selected) {
                _updateFilters(data);
            } else {
                _updateFilters();
            }
        },
        rowData: []
    };

    new agGrid.Grid($('.users-table').get(0), _usersGridOptions);
}

function _initHandlers() {
    $('.rooms-item-loader-btn').click(async function () {
        _showLoading();
        await _displayRooms(_selectedFilters, false);
        _hideLoading();
    });

    // for search to user
    $('.user-serach-box').keypress(function (event) {
        let _keycode = event.keyCode ? event.keyCode : event.which,
            _value = $(this).val().trim().toUpperCase();
        if (_keycode == '13' && _value) {
            _displayUser(_value);
        }
    });
    $('.searchbox-icon').click(function () {
        let _value = $('.user-serach-box').val().trim().toUpperCase();
        if (_value) {
            _displayUser(_value);
        }
    });

    // filter fold/unfold
    $('.user-filter-folder-btn.filter').click(function () {
        let _buttonContainer = $('.filter-buttons-container.filter');
        if (_buttonContainer.hasClass('unfold')) {
            $(this).removeClass('unfold');
            _buttonContainer.removeClass('unfold');
        } else {
            $(this).addClass('unfold');
            _buttonContainer.addClass('unfold');
        }
    });

    // Rooms filters
    $('.user-filter-btn').click((event) => {
        if ($(event.currentTarget).hasClass('disabled')) {
            return;
        }

        if ($(event.currentTarget).hasClass('selected')) {
            $(event.currentTarget).removeClass('selected');
        } else {
            $(event.currentTarget).addClass('selected');
        }

        const _filters = {};
        $('.user-filter-btn.selected').each(function () {
            _filters[$(this).attr('id')] = $(this).text();
        });

        _displayRooms(_filters, true);
    });

    // Save button
    $('.save-master-btn').click(() => {
        _applyRoomTransactions();
    });

    // init Noty
    PNotify.prototype.options.delay = 5000;
    PNotify.prototype.options.styling = 'bootstrap3';
}
