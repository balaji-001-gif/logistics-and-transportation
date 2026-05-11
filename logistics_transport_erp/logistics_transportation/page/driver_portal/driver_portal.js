frappe.pages['driver-portal'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Driver Portal',
        single_column: true
    });

    // Load the HTML content directly into the wrapper
    frappe.model.with_doctype('Driver', () => {
        $(wrapper).find('.layout-main-section').html(frappe.render_template('driver_portal', {}));
        LogisticsDriverPortal.init(wrapper);
    });
}

var LogisticsDriverPortal = {
    init: function(wrapper) {
        this.wrapper = wrapper;
        this.load_info();
        this.load_trips();
        this.bind_events();
    },

    load_info: function() {
        frappe.call({
            method: 'logistics_transport_erp.api.driver_portal_api.get_driver_info',
            callback: function(r) {
                if(r.message) {
                    $('#dp-driver-name').text(r.message.name);
                    $('#dp-vehicle-info').text('Vehicle: ' + (r.message.vehicle || '--'));
                    $('#dp-driver-status').text(r.message.status);
                }
            }
        });
    },

    load_trips: function() {
        var me = this;
        frappe.call({
            method: 'logistics_transport_erp.api.driver_portal_api.get_assigned_trips',
            callback: function(r) {
                var trips = r.message || [];
                var activeTrip = trips.find(t => t.status !== 'Completed');
                
                if (activeTrip) {
                    $('#dp-trip-id').text(activeTrip.name);
                    $('#dp-trip-status').text('Status: ' + activeTrip.status);
                    me.active_trip = activeTrip.name;
                } else {
                    $('#dp-active-trip-section').hide();
                }

                var listHtml = trips.map(t => `
                    <div class="dp-trip-item">
                        <div>
                            <strong>${t.name}</strong><br>
                            <small>${t.trip_date}</small>
                        </div>
                        <span class="badge ${t.status === 'Completed' ? 'badge-success' : 'badge-warning'}">${t.status}</span>
                    </div>
                `).join('');
                $('#dp-trip-list').html(listHtml || '<p>No recent trips.</p>');
            }
        });
    },

    bind_events: function() {
        var me = this;
        $('#btn-update-status').on('click', function() {
            $('#modal-status').show();
        });

        $('#btn-submit-status').on('click', function() {
            var event_type = $('#sel-event-type').val();
            var remarks = $('#txt-remarks').val();
            
            // Get GPS coordinates
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function(pos) {
                    me.submit_status(event_type, pos.coords.latitude, pos.coords.longitude, remarks);
                }, function(err) {
                    frappe.show_alert({message: 'GPS access denied. Submitting without location.', indicator: 'orange'});
                    me.submit_status(event_type, null, null, remarks);
                });
            } else {
                me.submit_status(event_type, null, null, remarks);
            }
        });
    },

    submit_status: function(event_type, lat, lng, remarks) {
        var me = this;
        frappe.call({
            method: 'logistics_transport_erp.api.driver_portal_api.update_trip_status',
            args: {
                trip_name: me.active_trip,
                event_type: event_type,
                lat: lat,
                lng: lng,
                remarks: remarks
            },
            callback: function(r) {
                if (r.message.status === 'success') {
                    frappe.show_alert({message: 'Status Updated!', indicator: 'green'});
                    $('#modal-status').hide();
                    me.load_trips();
                }
            }
        });
    }
}
