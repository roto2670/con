const LICENSE_KEY =
    'CompanyName=Kith Creative Inc.,LicensedApplication=SCS,LicenseType=SingleApplication,LicensedConcurrentDeveloperCount=1,LicensedProductionInstancesCount=0,AssetReference=AG-015479,ExpiryDate=9_May_2022_[v2]_MTY1MjA1MDgwMDAwMA==94d947d25667951aa892d1334d29ff9b';
const GRID_OPTIONS = {
    animateRows: true,
    defaultColDef: {
        flex: 1,
        sortable: false,
        resizable: true,
        editable: false,
        filter: false,
        suppressMenu: true,
        type: 'numericColumn',
        valueFormatter: (params) => {
            return _toNumberString(params.value);
        }
    },
    columnDefs: [
        {
            headerName: 'Camp',
            field: 'name'
        },
        {
            headerName: '',
            children: [
                {
                    headerName: 'Total',
                    valueGetter: (params) => {
                        return params.data?.total;
                    }
                },
                {
                    headerName: 'Occupancy',
                    valueGetter: (params) => {
                        return params.data?.occupancy;
                    }
                }
            ]
        },
        {
            headerName: 'AG',
            field: 'ag',
            children: [
                {
                    headerName: 'Total',
                    valueGetter: (params) => {
                        return params.data?.ag?.total;
                    }
                },
                {
                    headerName: 'Occupancy',
                    valueGetter: (params) => {
                        return params.data?.ag?.occupancy;
                    }
                }
            ]
        },
        {
            headerName: 'UG',
            field: 'ug',
            children: [
                {
                    headerName: 'Total',
                    valueGetter: (params) => {
                        return params.data?.ug?.total;
                    }
                },
                {
                    headerName: 'Occupancy',
                    valueGetter: (params) => {
                        return params.data?.ug?.occupancy;
                    }
                }
            ]
        },
        {
            headerName: 'Common',
            field: 'common',
            children: [
                {
                    headerName: 'Total',
                    valueGetter: (params) => {
                        return params.data?.common?.total;
                    }
                },
                {
                    headerName: 'Occupancy',
                    valueGetter: (params) => {
                        return params.data?.common?.occupancy;
                    }
                }
            ]
        }
    ],
    getRowNodeId: (data) => {
        return data.id;
    }
};

const _db = firebase.database();
let _campGridOptions = {},
    _usageGridOptions = {};

// Init
_initGrids();
_initHandlers();

_display();

function _loadData() {
    _db.ref('stats/camp/daily').on('value', (snapshot) => {
        const _data = snapshot.val();

        _updateData(_campGridOptions.api, _data.camps);
        _updateData(_usageGridOptions.api, _data.usages);
    });
}

function _updateData(api, campMap) {
    const _transaction = {
        add: [],
        update: []
    };

    _.each(campMap, (data, name) => {
        data.name = name;
        data.id = name;

        const _row = api.getRowNode();
        if (_row) {
            // Update
            _transaction.update.push(data);
        } else {
            _transaction.add.push(data);
        }
    });

    api.applyTransaction(_transaction);
}

function _initGrids() {
    agGrid.LicenseManager.setLicenseKey(LICENSE_KEY);

    _initCampGrid();
    _initUsageGrid();
}

function _initCampGrid() {
    _campGridOptions = _.clone(GRID_OPTIONS);
    new agGrid.Grid($('.cd-grid.camp').get(0), _campGridOptions);
}

function _initUsageGrid() {
    _usageGridOptions = _.clone(GRID_OPTIONS);
    new agGrid.Grid($('.cd-grid.usage').get(0), _usageGridOptions);
}

function _display() {
    _loadData();
}

function _initHandlers() {
    $('.cd-sub-title-btn').click(function () {
        if ($(this).parent().hasClass('unfold')) {
            $(this).parent().removeClass('unfold');
        } else {
            $(this).parent().addClass('unfold');
        }
    });
}

function _toNumberString(number) {
    return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}
