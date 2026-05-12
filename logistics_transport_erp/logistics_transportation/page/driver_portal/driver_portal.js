var LogisticsDriverPortal = {
    init: function(wrapper) {
        this.wrapper = wrapper;
        this.$wrapper = $(wrapper);
        this.load_info();
        this.load_trips();
        this.bind_events();
    },

    load_info: function() {
        var me = this;
        frappe.call({
            method: 'logistics_transport_erp.api.driver_portal_api.get_driver_info',
            callback: function(r) {
                if(r.message) {
                    me.$wrapper.find('#dp-driver-name').text(r.message.name);
                    me.$wrapper.find('#dp-vehicle-info').text('Vehicle: ' + (r.message.vehicle || '--'));
                    me.$wrapper.find('#dp-driver-status').text(r.message.status);
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
                    me.$wrapper.find('#dp-trip-id').text(activeTrip.name);
                    me.$wrapper.find('#dp-trip-status').text('Status: ' + activeTrip.status);
                    me.$wrapper.find('#dp-active-trip-section').show();
                    me.active_trip = activeTrip.name;
                } else {
                    me.$wrapper.find('#dp-active-trip-section').hide();
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
                me.$wrapper.find('#dp-trip-list').html(listHtml || '<p>No recent trips.</p>');
            }
        });
    },

    bind_events: function() {
        var me = this;
        me.$wrapper.on('click', '#btn-update-status', function() {
            me.$wrapper.find('#modal-status').css('display', 'flex');
        });

        me.$wrapper.on('click', '#btn-close-modal', function() {
            me.$wrapper.find('#modal-status').hide();
        });

        me.$wrapper.on('click', '#btn-submit-status', function() {
            var event_type = me.$wrapper.find('#sel-event-type').val();
            var remarks = me.$wrapper.find('#txt-remarks').val();
            
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
                if (r.message && r.message.status === 'success') {
                    frappe.show_alert({message: 'Status Updated!', indicator: 'green'});
                    me.$wrapper.find('#modal-status').hide();
                    me.load_trips();
                }
            }
        });
    }
}

frappe.pages['driver-portal'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Driver Portal',
        single_column: true
    });

    LogisticsDriverPortal.init(wrapper);
}
