
'use strict';
// merchant_id

var merchant_id = $("#merchant_id").val();
var package_merchant = $("#package_merchant").val();
var create_at = $("#create_at").val();
var today = new Date();
var time_after_send = parseInt($("#time_after_send").val());
if (!time_after_send) {
	time_after_send = 7;
}

if (package_merchant == "Acquire"){
	document.getElementById("block_acquire").style.display = 'none';
}
// time current


// tooltip
$("#tooltip1").tooltip({
	"title": ngettext("Tong_so_khach_hang_trong_khoang_thoi_gian_da_chon"),
	"animation": true,

});
$("#tooltip_contacts_collect").tooltip({
	"title": ngettext("Tong_so_khach_hang_moi_va_co_lien_he_trong_khoang_thoi_gian_da_chon"),
	"animation": true,

});
$("#tooltip_crr").tooltip({
	"title": ngettext("Ty_le_khach_hang_quay_lai_trong_mot_khoang_thoi_gian_nhat_dinh"),
	"animation": true,

});
$("#tooltip_customers").tooltip({
	"title": ngettext("Thong_ke_chi_tiet_ve_tong_so_khach_hang,_khach_hang_moi_va_khach_hang_quay_lai_trong_mot_khoang_thoi_gian_nhat_dinh"),
	"animation": true,

});
// $("#tooltip_churnrate").tooltip({
// 	"title": "Tỷ lệ khách hàng không quay lại trong một khoảng thời gian nhất định",
// 	"animation": true,
//
// });
$("#tooltip_cross_shopers").tooltip({
	"title": ngettext("Ty_le_khach_hang_da_den_cac_dia_diem_khac_trong_chuoi"),
	"animation": true,

});
// $("#tooltip_clv").tooltip({
// 	"title": "Doanh thu mà một khách hàng sẽ tạo ra trong suốt vòng đời của họ",
// 	"animation": true,
//
// });
$("#tooltip_new_customer_percent").tooltip({
	"title": ngettext("Ty_le_khach_hang_moi_so_voi_tong_so_khach_hang"),
	"animation": true,

});
$("#tooltip_customer_comeback_percent").tooltip({
	"title": ngettext("Ty_le_khach_hang_quay_lai_so_voi_tong_so_khach_hang"),
	"animation": true,

});
$("#tooltip_avpv").tooltip({
	"title": ngettext("Trung_binh_so_luot_den_cua_1_khach_hang"),
	"animation": true,

});
$("#tooltip2").tooltip({
	"title": ngettext("Khach_hang_moi_trong_khoang_thoi_gian_da_chon"),
	"animation": true,

});
$("#tooltip3").tooltip({
	"title": ngettext("tong_khach_hang_quay_lai_trong_khoang_thoi_gian_da_chon"),
	"animation": true,

});
$("#tooltip4").tooltip({
	"title": ngettext("Tong_so_luot_khach_den_trong_khoang_thoi_gian_da_chon"),
	"animation": true,

});
$("#tooltip5").tooltip({
	"title": ngettext("Loi_nhuan_uoc_tinh_dua_tren_so_khach_quay_lai_va_trung_binh_chi_tieu_1_khach_(hoa_don_trung_binh)._Nhap_trong_phan_CAI_DAT"),
	"animation": true,

});
$("#tooltip6").tooltip({
	"title": ngettext("So_coupon_da_tao_va_da_duoc_doi_(co_su_dung)_trong_khoang_thoi_gian_da_chon"),
	"animation": true,

});
$("#tooltip7").tooltip({
	"title": ngettext("Khach_hang_quay_lai_sau_khi_nhan_duoc_tin_nhan_tu_bat_ki_kenh_nao_(sms,_zalo,_chatbot,_email...),_ke_tu") + time_after_send + ngettext("ngay_truoc_(truoc_ngay_bat_dau_xem_bao_cao)_nhap_ngay_trong_phan_cai_dat"),
	"animation": true,

});

$("#tooltip8").tooltip({
	"title": ngettext("So_luot_truy_cap_wifi_theo_thiet_bi"),
	"animation": true,

});

$("#tooltip9").tooltip({
	"title": ngettext("So_luong_khach_hang_theo_cac_nguon"),
	"animation": true,

});
$("#tooltip10").tooltip({
	"title": ngettext("So_luong_khach_hang_theo_luot_den_(mac_dinh_cac_luot_den_1,_2,_3_den_9_va_tren_10_luot),_don_vi_tinh_quy_doi_theo_%"),
	"animation": true,

})
$("#tooltip11").tooltip({
	"title": ngettext("So_luong_khach_hang_theo_cac_khung_gio_trong_ngay,_don_vi_quy_doi_theo_%"),
	"animation": true,

})
$("#tooltip12").tooltip({
	"title": ngettext("So_luong_khach_hang_theo_cac_ngay_trong_tuan_(cac_thu_trong_tuan),_don_vi_quy_doi_theo_%"),
	"animation": true,

})
$("#tooltip13").tooltip({
	"title": ngettext("So_luong_tin_nhan_da_gui_tu_tat_ca_cac_kenh_nhu:_SMS,_ZALO,_MESSAGE,_EMAIL"),
	"animation": true,

})


'use strict';

'use strict';

var $map = $('#map-canvas'),
	map,
	lat,
	lng,
	color = "#5e72e4";

'use strict';


'use strict';


'use strict';

'use strict';

'use strict';

'use strict';
var Charts = (function () {
	// Variable
	var $toggle = $('[data-toggle="chart"]');
	var mode = 'light'; //(themeMode) ? themeMode : 'light';
	var fonts = {
		base: 'Open Sans'
	}
	// Colors
	var colors = {
		gray: {
			100: '#f6f9fc',
			200: '#e9ecef',
			300: '#dee2e6',
			400: '#ced4da',
			500: '#adb5bd',
			600: '#8898aa',
			700: '#525f7f',
			800: '#32325d',
			900: '#212529'
		},
		theme: {
			'default': '#172b4d',
			'primary': '#5e72e4',
			'secondary': '#f4f5f7',
			'info': '#11cdef',
			'success': '#2dce89',
			'danger': '#f5365c',
			'warning': '#fb6340'
		},
		black: '#12263F',
		white: '#FFFFFF',
		transparent: 'transparent',
	};
	// Methods
	// Chart.js global options
	function chartOptions() {
		// Options
		var options = {
			defaults: {
				global: {
					responsive: true,
					maintainAspectRatio: false,
					defaultColor: (mode == 'dark') ? colors.gray[700] : colors.gray[600],
					defaultFontColor: (mode == 'dark') ? colors.gray[700] : colors.gray[600],
					defaultFontFamily: fonts.base,
					defaultFontSize: 13,
					layout: {
						padding: 0
					},
					legend: {
						display: false,
						position: 'bottom',
						labels: {
							usePointStyle: true,
							padding: 16
						}
					},
					elements: {
						point: {
							radius: 0,
							backgroundColor: colors.theme['primary']
						},
						line: {
							tension: .4,
							borderWidth: 4,
							borderColor: colors.theme['primary'],
							backgroundColor: colors.transparent,
							borderCapStyle: 'rounded'
						},
						rectangle: {
							backgroundColor: colors.theme['warning']
						},
						arc: {
							backgroundColor: colors.theme['primary'],
							borderColor: (mode == 'dark') ? colors.gray[800] : colors.white,
							borderWidth: 4
						}
					},
					tooltips: {
						enabled: false,
						mode: 'index',
						intersect: false,
						custom: function (model) {

							// Get tooltip
							var $tooltip = $('#chart-tooltip');

							// Create tooltip on first render
							if (!$tooltip.length) {
								$tooltip = $('<div id="chart-tooltip" class="popover bs-popover-top" role="tooltip"></div>');

								// Append to body
								$('body').append($tooltip);
							}

							// Hide if no tooltip
							if (model.opacity === 0) {
								$tooltip.css('display', 'none');
								return;
							}

							function getBody(bodyItem) {
								return bodyItem.lines;
							}

							// Fill with content
							if (model.body) {
								var titleLines = model.title || [];
								var bodyLines = model.body.map(getBody);
								var html = '';

								// Add arrow
								html += '<div class="arrow"></div>';

								// Add header
								titleLines.forEach(function (title) {
									html += '<h3 class="popover-header text-center">' + title + '</h3>';
								});

								// Add body
								bodyLines.forEach(function (body, i) {
									var colors = model.labelColors[i];
									var styles = 'background-color: ' + colors.backgroundColor;
									var indicator = '<span class="badge badge-dot"><i class="bg-primary"></i></span>';
									var align = (bodyLines.length > 1) ? 'justify-content-left' : 'justify-content-center';
									html += '<div class="popover-body d-flex align-items-center ' + align + '">' + indicator + body + '</div>';
								});

								$tooltip.html(html);
							}

							// Get tooltip position
							var $canvas = $(this._chart.canvas);

							var canvasWidth = $canvas.outerWidth();
							var canvasHeight = $canvas.outerHeight();

							var canvasTop = $canvas.offset().top;
							var canvasLeft = $canvas.offset().left;

							var tooltipWidth = $tooltip.outerWidth();
							var tooltipHeight = $tooltip.outerHeight();

							var top = canvasTop + model.caretY - tooltipHeight - 16;
							var left = canvasLeft + model.caretX - tooltipWidth / 2;

							// Display tooltip
							$tooltip.css({
								'top': top + 'px',
								'left': left + 'px',
								'display': 'block',
								'z-index': '100'
							});

						},
						callbacks: {
							label: function (item, data) {
								var label = data.datasets[item.datasetIndex].label || '';
								var yLabel = item.yLabel;
								var content = '';

								if (data.datasets.length > 1) {
									content += '<span class="badge badge-primary mr-auto">' + label + '</span>';
								}

								content += '<span class="popover-body-value">' + yLabel + '</span>';
								return content;
							}
						}
					}
				},
				doughnut: {
					cutoutPercentage: 83,
					tooltips: {
						callbacks: {
							title: function (item, data) {
								var title = data.labels[item[0].index];
								return title;
							},
							label: function (item, data) {
								var value = data.datasets[0].data[item.index];
								var content = '';

								content += '<span class="popover-body-value">' + value + '</span>';
								return content;
							}
						}
					},
					legendCallback: function (chart) {
						var data = chart.data;
						var content = '';

						data.labels.forEach(function (label, index) {
							var bgColor = data.datasets[0].backgroundColor[index];

							content += '<span class="chart-legend-item">';
							content += '<i class="chart-legend-indicator" style="background-color: ' + bgColor + '"></i>';
							content += label;
							content += '</span>';
						});

						return content;
					}
				}
			}
		}

		// yAxes
		Chart.scaleService.updateScaleDefaults('linear', {
			gridLines: {
				borderDash: [2],
				borderDashOffset: [2],
				color: (mode == 'dark') ? colors.gray[900] : colors.gray[300],
				drawBorder: false,
				drawTicks: false,
				lineWidth: 0,
				zeroLineWidth: 0,
				zeroLineColor: (mode == 'dark') ? colors.gray[900] : colors.gray[300],
				zeroLineBorderDash: [2],
				zeroLineBorderDashOffset: [2]
			},
			ticks: {
				beginAtZero: true,
				padding: 10,
				callback: function (value) {
					if (!(value % 10)) {
						return value
					}
				}
			}
		});

		// xAxes
		Chart.scaleService.updateScaleDefaults('category', {
			gridLines: {
				drawBorder: false,
				drawOnChartArea: false,
				drawTicks: false
			},
			ticks: {
				padding: 20
			},
			maxBarThickness: 10
		});

		return options;

	}

	// Parse global options
	function parseOptions(parent, options) {
		for (var item in options) {
			if (typeof options[item] !== 'object') {
				parent[item] = options[item];
			} else {
				parseOptions(parent[item], options[item]);
			}
		}
	}

	// Push options
	function pushOptions(parent, options) {
		for (var item in options) {
			if (Array.isArray(options[item])) {
				options[item].forEach(function (data) {
					parent[item].push(data);
				});
			} else {
				pushOptions(parent[item], options[item]);
			}
		}
	}

	// Pop options
	function popOptions(parent, options) {
		for (var item in options) {
			if (Array.isArray(options[item])) {
				options[item].forEach(function (data) {
					parent[item].pop();
				});
			} else {
				popOptions(parent[item], options[item]);
			}
		}
	}

	// Toggle options
	function toggleOptions(elem) {
		var options = elem.data('add');
		var $target = $(elem.data('target'));
		var $chart = $target.data('chart');

		if (elem.is(':checked')) {

			// Add options
			pushOptions($chart, options);

			// Update chart
			$chart.update();
		} else {

			// Remove options
			popOptions($chart, options);

			// Update chart
			$chart.update();
		}
	}

	// Update options
	function updateOptions(elem) {
		var options = elem.data('update');
		var $target = $(elem.data('target'));
		var $chart = $target.data('chart');

		// Parse options
		parseOptions($chart, options);

		// Toggle ticks
		toggleTicks(elem, $chart);

		// Update chart
		$chart.update();
	}

	// Toggle ticks
	function toggleTicks(elem, $chart) {

		if (elem.data('prefix') !== undefined || elem.data('prefix') !== undefined) {
			var prefix = elem.data('prefix') ? elem.data('prefix') : '';
			var suffix = elem.data('suffix') ? elem.data('suffix') : '';

			// Update ticks
			$chart.options.scales.yAxes[0].ticks.callback = function (value) {
				if (!(value % 10)) {
					return prefix + value + suffix;
				}
			}

			// Update tooltips
			$chart.options.tooltips.callbacks.label = function (item, data) {
				var label = data.datasets[item.datasetIndex].label || '';
				var yLabel = item.yLabel;
				var content = '';

				if (data.datasets.length > 1) {
					content += '<span class="popover-body-label mr-auto">' + label + '</span>';
				}

				content += '<span class="popover-body-value">' + prefix + yLabel + suffix + '</span>';
				return content;
			}

		}
	}
	// Events
	// Parse global options
	if (window.Chart) {
		parseOptions(Chart, chartOptions());
	}
	// Toggle options
	$toggle.on({
		'change': function () {
			var $this = $(this);

			if ($this.is('[data-add]')) {
				toggleOptions($this);
			}
		},
		'click': function () {
			var $this = $(this);

			if ($this.is('[data-update]')) {
				updateOptions($this);
			}
		}
	});
	// Return
	return {
		colors: colors,
		fonts: fonts,
		mode: mode
	};

})();




//----


// Select2

$('#shop_in_mer').select2();
$('#shop_in_mer').on('change.select2', function (e) {
	cb(start, end);
});
// Chọn theo ngày

function toTimestamp(strDate) {
	var datum = Date.parse(strDate);
	return datum / 1000;
}

var start = moment().subtract(6, 'days');
var end = moment();

function cb(start, end) {
	start.set({hour:0,minute:0,second:0,millisecond:0});
	end.set({hour:23,minute:59,second:59,millisecond:0});
	$("#total_customer").hide();
	$("#new_customer").hide();
	$("#customer_comeback").hide();
	$("#total_visit").hide();
	$("#average_earnings").hide();
	$("#coupon_redeemed").hide();
	$("#coupon_redeem").hide();
	$("#customer_comeback_after").hide();
	$("#chart_sales").hide();
	$("#top_shop").hide();
	$("#top_shop_count").hide();
	$("#low_shop").hide();
	$("#low_shop_count").hide();
	$("#new_customer_percent").hide();
	$("#customer_comeback_percent").hide();
	$("#avpv").hide();
	// $("#clv").hide();
	// $("#clv_load").show();
	// $("#crr").hide();
	// $("#churnrate_crr").hide();
	$("#cross_shopers").hide();
	$("#contacts_collect").hide();
	$("#customers").hide();

	$("#total_customer_avg").hide();
	$("#new_customer_avg").hide();
	$("#customer_comeback_avg").hide();
	$("#total_visit_avg").hide();
	$("#average_earnings_avg").hide();
	$("#coupon_redeemed_avg").hide();
	$("#coupon_redeem_avg").hide();
	$("#customer_comeback_after_avg").hide();

	$("#total_customer_load").show();
	$("#new_customer_load").show();
	$("#customer_comeback_load").show();
	$("#total_visit_load").show();
	$("#average_earnings_load").show();
	$("#coupon_redeemed_load").show();
	$("#coupon_redeem_load").show();
	$("#chart_sales_load").show();
	$("#customer_comeback_after_load").show();
	$("#top_shop_load").show();
	$("#top_shop_count_load").show();
	$("#low_shop_load").show();
	$("#low_shop_count_load").show();
	$("#cross_shopers_load").show();
	$("#contacts_collect_load").show();
	$("#new_customer_percent_load").show();
	$("#customer_comeback_percent_load").show();
	$("#avpv_load").show();
	$("#crr_load").show();
	// $("#churnrate_load").show();
	$("#customers_load").show();

	$("#total_customer_avg_load").show();
	$("#new_customer_avg_load").show();
	$("#customer_comeback_avg_load").show();
	$("#total_visit_avg_load").show();
	$("#average_earnings_avg_load").show();
	$("#coupon_redeemed_avg_load").show();
	$("#coupon_redeem_avg_load").show();
	$("#customer_comeback_after_avg_load").show();

	var shop_id = $("#shop_in_mer").val();
	var date_start = toTimestamp(start);
	var date_end = toTimestamp(end);
	$('#reportrange span').html(start.format('DD/MM/YYYY') + ' - ' + end.format('DD/MM/YYYY'));

	function getDates(start, end) {
		var dateArray = [];
		var currentDate = moment(start);
		var stopDate = moment(end);
		while (currentDate <= stopDate) {
			dateArray.push(moment(currentDate).format('DD/MM'));
			currentDate = moment(currentDate).add(1, 'days');
		}
		return dateArray;
	};
	function get_list_date(start, end) {
		var dateArray = [];
		var currentDate = moment(start);
		var stopDate = moment(end);
		while (currentDate <= stopDate) {
			dateArray.push('"' + moment(currentDate).format('MM/DD/YY') + '"')
			currentDate = moment(currentDate).add(1, 'days');
		}
		return dateArray;
	};

	function update_chart(chart, label, data) {
		chart.data.labels = label;
		chart.data.datasets[0].data = data;
		chart.update();
	};

	//----  Top Shop

	if (shop_id == "all") {
		var location = `query{
			location(merchantId:"`+ String(merchant_id) + `", dateStart: ` + date_start + `, dateEnd: ` + date_end + `)
			{
				topShop
				topShopCut
			    topShopCount
			    lowShop
			    lowShopCut
			    lowShopCount
			  }
			}`;
	} else {
		var location = `query{
			location(shopId:"`+ String(shop_id) + `", dateStart: ` + date_start + `, dateEnd: ` + date_end + `)
			{
				topShop
				topShopCut
			    topShopCount
			    lowShop
			    lowShopCut
			    lowShopCount
			  }
			}`;
	};
	async function location_count() {
		await fetch('https://report.nextify.vn/graphql', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Accept': 'application/json',
			},
			body: JSON.stringify({ query: location })
		}).then(r => { return r.json() }).then(data_lc => {
			var data_lc = data_lc;
			$("#top_shop_load").hide();
			$("#top_shop_count_load").hide();
			$("#low_shop_load").hide();
			$("#low_shop_count_load").hide();
			document.getElementById("top_shop").innerHTML = data_lc.data.location.topShop;
			document.getElementById("top_shop_count").innerHTML = data_lc.data.location.topShopCount;
			document.getElementById("low_shop").innerHTML = data_lc.data.location.lowShop;
			document.getElementById("low_shop_count").innerHTML = data_lc.data.location.lowShopCount;

			$("#top_shop").show();
			$("#top_shop_count").show();
			$("#low_shop").show();
			$("#low_shop_count").show();
		})
	};
	location_count();

	//----  Cross Shopers

	if (shop_id != "all") {
		var cross = `query{
				cross(shopId:"`+ String(shop_id) + `", dateStart: ` + date_start + `, dateEnd: ` + date_end + `)
				{
					result
				  }
				}`;
	}
	else {
		var cross = `query{
			cross(merchantId:"`+ String(merchant_id) + `", dateStart: ` + date_start + `, dateEnd: ` + date_end + `)
			{
				result
			  }
			}`;
	};
	async function cross_shopers() {
		await fetch('https://report.nextify.vn/graphql', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Accept': 'application/json',
			},
			body: JSON.stringify({ query: cross })
		}).then(r => { return r.json() }).then(data_ls => {
			$("#cross_shopers_load").hide();
			var data_ls = data_ls;
			var labes_arr = ["Cross Shopers", "Other"];
			var data_arr = []
			data_arr.push(data_ls.data.cross.result);
			data_arr.push(100 - data_ls.data.cross.result);
			update_chart(cross_shopers_chart, labes_arr, data_arr)
			$("#cross_shopers").show();
		})
	};
	cross_shopers();

	//----  Contact Collect

	if (shop_id != "all") {
		var contact = `query{
			contactCrr(shopId:"`+ String(shop_id) + `", dateStart: ` + date_start + `, dateEnd: ` + date_end + `)
			{
				contactCollect
				other
			  }
			}`;
	}
	else {
		var contact = `query{
			contactCrr(merchantId:"`+ String(merchant_id) + `", dateStart: ` + date_start + `, dateEnd: ` + date_end + `)
			{
				contactCollect
				other
			  }
			}`;
	};
	async function contacts_collect() {
		await fetch('https://report.nextify.vn/graphql', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Accept': 'application/json',
			},
			body: JSON.stringify({ query: contact })
		}).then(r => { return r.json() }).then(data_ls => {
			$("#contacts_collect_load").hide();
			var labes_arr = [ngettext("Khach_hang_co_lien_He"), ngettext("Khach_hang_khong_co_lien_He")];
			var data_arr = []
			data_arr.push(data_ls.data.contactCrr.contactCollect);
			data_arr.push(data_ls.data.contactCrr.other);
			update_chart(contacts_collect_chart, labes_arr, data_arr)
			$("#contacts_collect").show();
		})
	};
	contacts_collect();

	//----  khách quay lại sau xem tin nhắn

	if (shop_id != "all") {
		var data_customers_after = `query{
				sendactivity(merchantId:"`+ String(merchant_id) + `", dateStart: ` + date_start + `, dateEnd: ` + date_end + `, timeSetting:` + time_after_send + `)
				{
					customersReceiverCb
					customersReceiverPercent
				  }
				}`;
	}
	else {
		var data_customers_after = `query{
			sendactivity(merchantId:"`+ String(merchant_id) + `", dateStart: ` + date_start + `, dateEnd: ` + date_end + `, timeSetting:` + time_after_send + `)
			{
				customersReceiverCb
				customersReceiverPercent
			  }
			}`;
	};
	async function cus_after_seen() {
		await fetch('https://report.nextify.vn/graphql', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Accept': 'application/json',
			},
			body: JSON.stringify({ query: data_customers_after })
		}).then(r => { return r.json() }).then(data_ls => {
			var data_ls = data_ls.data.sendactivity;
			$("#customer_comeback_after_load").hide();
			$("#customer_comeback_after").show();
			document.getElementById("customer_comeback_after").innerHTML = data_ls.customersReceiverPercent;
			$("#customer_comeback_after_avg_load").hide();
			$("#customer_comeback_after_avg").show();
			document.getElementById("customer_comeback_after_avg").innerHTML = parseInt(data_ls.customersReceiverCb / get_list_date(start, end).length);
		})
	};
	cus_after_seen();
	//---- tổng khách theo năm

	if (shop_id != "all") {
		var data_customers = `query{
				requestshop(shopId:"`+ String(shop_id) + `", listDate: [` + get_list_date(start, end) + `])
				{	when
					totalCustomers
				}}`;
		async function total_cus_year() {
			await fetch('https://report.nextify.vn/graphql', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'Accept': 'application/json',
				},
				body: JSON.stringify({ query: data_customers })
			}).then(r => { return r.json() }).then(data_res => {
				$("#chart_sales_load").hide();
				var data_ls = data_res.data.requestshop;
				var i = 0;
				var result = [];
				for (i = 0; i < get_list_date(start, end).length; i++) {
					if (i < data_ls.length) {
						result[get_list_date(start, end).indexOf('"' + data_ls[i].when + '"')] = data_ls[i].totalCustomers;
					}
				}
				for (i = 0; i < get_list_date(start, end).length; i++) {
					if (result[i] == undefined) {
						result[i] = 0;
					}
				}
				update_chart(chart_sales_chart, getDates(start, end), result);
				$("#chart_sales").show();
			});
		};
		total_cus_year();
	}
	else {
		var data_customers = `query{
			request(merchantId:"`+ String(merchant_id) + `", listDate: [` + get_list_date(start, end) + `])
			{	when
				totalCustomers
			}}`;
		async function total_cus_year() {
			await fetch('https://report.nextify.vn/graphql', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'Accept': 'application/json',
				},
				body: JSON.stringify({ query: data_customers })
			}).then(r => { return r.json() }).then(data_res => {
				$("#chart_sales_load").hide();
				var data_ls = data_res.data.request;
				var i = 0;
				var result = [];
				for (i = 0; i < get_list_date(start, end).length; i++) {
					if (i < data_ls.length) {
						result[get_list_date(start, end).indexOf('"' + data_ls[i].when + '"')] = data_ls[i].totalCustomers;
					}
				}
				for (i = 0; i < get_list_date(start, end).length; i++) {
					if (result[i] == undefined) {
						result[i] = 0;
					}
				}
				update_chart(chart_sales_chart, getDates(start, end), result);
				$("#chart_sales").show();
			});
		};
		total_cus_year();
	};
	// điểm đông nhất - thấp nhất


	// tổng số lượt đến

	if (shop_id != "all") {
		var data_visit = `query{
				visitbytime(shopId:"`+ String(shop_id) + `" , dateStart: ` + date_start + `, dateEnd: ` + date_end + `)
				{
					visits
					visitsEx
				  }
				}`
	}
	else {
		var data_visit = `query{
			visitbytime(merchantId:"`+ String(merchant_id) + `" , dateStart: ` + date_start + `, dateEnd: ` + date_end + `)
			{
				visits
				visitsEx
			  }
			}`
	}
	async function cus_total_visit() {
		await fetch('https://report.nextify.vn/graphql', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Accept': 'application/json',
			},
			body: JSON.stringify({ query: data_visit })
		}).then(r => { return r.json() }).then(data_res => {
			var data_ls = data_res.data.visitbytime;
			$("#total_visit_load").hide();
			$("#total_visit").show();
			document.getElementById("total_visit").innerHTML = data_ls.visits;
			document.getElementById("total_visit_day").innerHTML = parseInt(get_list_date(start, end).length) + " ";
			$("#total_visit_avg_load").hide();
			$("#total_visit_avg").show();
			document.getElementById("total_visit_avg").innerHTML = parseInt(data_ls.visits / get_list_date(start, end).length);
			if (data_ls.visitsEx > data_ls.visits) {
				if (data_ls.visits == 0) {
					document.getElementById("total_visit_per_down").innerHTML = `<i class="fa fa-arrow-down"></i> ` + 100 + " %";
				}
				else {
					document.getElementById("total_visit_per_down").innerHTML = `<i class="fa fa-arrow-down"></i> ` + (parseInt(data_ls.visitsEx - data_ls.visits) / data_ls.visitsEx * 100).toFixed(0) + " %";
				};
				$("#total_visit_per_up").hide();
				$("#total_visit_per_down").show();
			}
			else {
				if (data_ls.visitsEx == 0) {
					document.getElementById("total_visit_per_up").innerHTML = `<i class="fa fa-arrow-up"></i> ` + 100 + " %";
				}
				else {
					document.getElementById("total_visit_per_up").innerHTML = `<i class="fa fa-arrow-up"></i> ` + (parseInt(data_ls.visits - data_ls.visitsEx) / data_ls.visitsEx * 100).toFixed(0) + " %";
				};
				$("#total_visit_per_up").show();
				$("#total_visit_per_down").hide();
			};
			var average_earnings = $("#average_earnings_inp").val();
			if (!average_earnings || average_earnings.length <= 0){
				average_earnings = 200000;
			};
			$("#average_earnings_load").hide();
			$("#average_earnings").show();
			document.getElementById("average_earnings").innerHTML = (data_ls.visits * average_earnings).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
			$("#average_earnings_avg_load").hide();
			$("#average_earnings_avg").show();
			document.getElementById("average_earnings_avg").innerHTML = parseInt(data_ls.visits * average_earnings / get_list_date(start, end).length).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");

		})
	};
	cus_total_visit();
	// khách theo lượt đến

	var data_visitbytime = `query{
			request(merchantId:"`+ String(merchant_id) + `", listDate: [` + get_list_date(start, end) + `])
			{arrivalCustomers {
				typeArrival
				count
			}
			}
		}`
	if (shop_id != "all") {
		var data_visitbytime = `query{
				requestshop(shopId:"`+ String(shop_id) + `", listDate: [` + get_list_date(start, end) + `])
				{arrivalCustomers {
					typeArrival
					count
				}
				}
			}`;
		async function cus_visit_bytime() {
			await fetch('https://report.nextify.vn/graphql', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'Accept': 'application/json',
				},
				body: JSON.stringify({ query: data_visitbytime })
			}).then(r => { return r.json() }).then(data_res => {
				var data_resp = data_res.data.requestshop;
				var data_arr = ["1", "2", "3-9", "10+"];
				var data_1 = [];
				var data_2 = [];
				var data_9 = [];
				var data_10 = [];
				var i = 0;
				if (data_resp.length != 0) {
					for (i = 0; i < data_resp.length; i++) {
						var range_item = data_resp[i].arrivalCustomers;
						data_1.push(parseInt(range_item[0].count))
						data_2.push(parseInt(range_item[1].count))
						data_9.push(parseInt(range_item[2].count))
						data_10.push(parseInt(range_item[3].count))
					}
					var labes_arr1 = [parseInt((data_1.reduce((a, b) => a + b, 0)).toFixed(2)),
					parseInt((data_2.reduce((a, b) => a + b, 0)).toFixed(2)),
					parseInt((data_9.reduce((a, b) => a + b, 0)).toFixed(2)),
					parseInt((data_10.reduce((a, b) => a + b, 0)).toFixed(2))];
					var average1 = labes_arr1.reduce((a, b) => a + b, 0);
					if (average1 === 0) {
						update_chart(customers_by_visit_chart, data_arr, labes_arr1)
					}
					else {
						var labes_arr = [(labes_arr1[0] / average1 * 100).toFixed(0),
						(labes_arr1[1] / average1 * 100).toFixed(0),
						(labes_arr1[2] / average1 * 100).toFixed(0)
						];
						labes_arr.push(100 - (parseInt(labes_arr[0]) + parseInt(labes_arr[1]) + parseInt(labes_arr[2])));
						update_chart(customers_by_visit_chart, data_arr, labes_arr)
					}
				}

			})
		};
		cus_visit_bytime();
	}
	else {
		async function cus_visit_bytime() {
			await fetch('https://report.nextify.vn/graphql', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'Accept': 'application/json',
				},
				body: JSON.stringify({ query: data_visitbytime })
			}).then(r => { return r.json() }).then(data_res => {
				var data_resp = data_res.data.request;
				var data_arr = ["1", "2", "3-9", "10+"];
				var data_1 = [];
				var data_2 = [];
				var data_9 = [];
				var data_10 = [];
				var i = 0;
				if (data_resp.length != 0) {
					for (i = 0; i < data_resp.length; i++) {
						var range_item = data_resp[i].arrivalCustomers;
						data_1.push(parseInt(range_item[0].count))
						data_2.push(parseInt(range_item[1].count))
						data_9.push(parseInt(range_item[2].count))
						data_10.push(parseInt(range_item[3].count))
					}
					var labes_arr1 = [parseInt((data_1.reduce((a, b) => a + b, 0)).toFixed(2)),
					parseInt((data_2.reduce((a, b) => a + b, 0)).toFixed(2)),
					parseInt((data_9.reduce((a, b) => a + b, 0)).toFixed(2)),
					parseInt((data_10.reduce((a, b) => a + b, 0)).toFixed(2))];
					var average1 = labes_arr1.reduce((a, b) => a + b, 0);
					if (average1 === 0) {
						update_chart(customers_by_visit_chart, data_arr, labes_arr1)
					}
					else {
						var labes_arr = [(labes_arr1[0] / average1 * 100).toFixed(0),
						(labes_arr1[1] / average1 * 100).toFixed(0),
						(labes_arr1[2] / average1 * 100).toFixed(0)
						];
						labes_arr.push(100 - (parseInt(labes_arr[0]) + parseInt(labes_arr[1]) + parseInt(labes_arr[2])));
						update_chart(customers_by_visit_chart, data_arr, labes_arr)
					}
				}

			})
		};
		cus_visit_bytime()
	}

	// customer comback - new_customer - total_customers
	if (shop_id != "all") {
		var data_customer_comback = `query{
				customers(shopId:"`+ String(shop_id) + `" , dateStart: ` + date_start + `, dateEnd: ` + date_end + `)
				{
					customers
					customersCb
					newCustomers
					customersEx
					customersCbEx
					newCustomersEx
					totalVisits
				  }
				}`
	}
	else {
		var data_customer_comback = `query{
			customers(merchantId:"`+ String(merchant_id) + `" , dateStart: ` + date_start + `, dateEnd: ` + date_end + `)
			{
				customers
				customersCb
				newCustomers
				customersEx
				customersCbEx
				newCustomersEx
				totalVisits
			  }
			}`
	};

	async function cus_comback() {
		await fetch('https://report.nextify.vn/graphql', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Accept': 'application/json',
			},
			body: JSON.stringify({ query: data_customer_comback })
		}).then(r => { return r.json() }).then(data => {
			var result = data.data.customers;
			$("#total_customer_load").hide();
			$("#total_customer").show();
			document.getElementById("total_customer").innerHTML = result.customers;
			document.getElementById("total_customer_day").innerHTML = parseInt(get_list_date(start, end).length) + " ";
			$("#total_customer_avg_load").hide();
			$("#total_customer_avg").show();
			document.getElementById("total_customer_avg").innerHTML = parseInt(result.customers / get_list_date(start, end).length);
			if (result.customersEx > result.customers) {
				if (result.customers == 0) {
					document.getElementById("total_customer_per_down").innerHTML = `<i class="fa fa-arrow-down"></i> ` + 0 + " %";
				}
				else {
					document.getElementById("total_customer_per_down").innerHTML = `<i class="fa fa-arrow-down"></i> ` + ((result.customersEx - result.customers) / result.customersEx * 100).toFixed(0) + " %";
				}
				$("#total_customer_per_down").show();
				$("#total_customer_per_up").hide();
			}
			else {
				if (result.customersEx == 0) {
					document.getElementById("total_customer_per_up").innerHTML = `<i class="fa fa-arrow-up"></i> ` + 100 + " %";
				}
				else {
					document.getElementById("total_customer_per_up").innerHTML = `<i class="fa fa-arrow-up"></i> ` + ((result.customers - result.customersEx) / result.customersEx * 100).toFixed(0) + " %";
				}
				$("#total_customer_per_up").show();
				$("#total_customer_per_down").hide();
			};

			var newCustomers = result.newCustomers;
			var customersCb = result.customersCb;

			// $("#customer_comeback_load").hide();
			// $("#customer_comeback_percent_load").hide();
			// $("#customer_comeback").show();
			// $("#customer_comeback_percent").show();
			// document.getElementById("customer_comeback").innerHTML = result.customersCb;
			// if (result.customers != 0) {
			// 	document.getElementById("customer_comeback_percent").innerHTML = (result.customersCb / result.customers * 100).toFixed(0) + '%';
			// } else {
			// 	document.getElementById("customer_comeback_percent").innerHTML = '0%';
			// };
			// document.getElementById("customer_comeback_day").innerHTML = parseInt(get_list_date(start, end).length) + " ";
			// $("#customer_comeback_avg_load").hide();
			// $("#customer_comeback_avg").show();
			// document.getElementById("customer_comeback_avg").innerHTML = parseInt(result.customersCb / get_list_date(start, end).length);
			if (result.customersCbEx > result.customersCb) {
			// 	if (result.customersCb == 0) {
			// 		document.getElementById("customer_comeback_per_down").innerHTML = `<i class="fa fa-arrow-down"></i> ` + 100 + " %";
			// 		document.getElementById("average_earnings_per_down").innerHTML = `<i class="fa fa-arrow-down"></i> ` + 100 + " %";
			// 	}
			// 	else {
			// 		document.getElementById("customer_comeback_per_down").innerHTML = `<i class="fa fa-arrow-down"></i> ` + ((result.customersCbEx - result.customersCb) / result.customersCbEx * 100).toFixed(0) + " %";
			// 		document.getElementById("average_earnings_per_down").innerHTML = `<i class="fa fa-arrow-down"></i> ` + ((result.customersCbEx - result.customersCb) / result.customersCbEx * 100).toFixed(0) + " %";
			// 	}
			// 	$("#customer_comeback_per_down").show();
			// 	$("#customer_comeback_per_up").hide();
				document.getElementById("average_earnings_day").innerHTML = parseInt(get_list_date(start, end).length) + " ";
				$("#average_earnings_per_up").hide();
				$("#average_earnings_per_down").show();
			}
			else {
			// 	if (result.customersCbEx == 0) {
			// 		document.getElementById("customer_comeback_per_up").innerHTML = `<i class="fa fa-arrow-up"></i> ` + 100 + " %";
			// 		document.getElementById("average_earnings_per_up").innerHTML = `<i class="fa fa-arrow-up"></i> ` + 100 + " %";
			// 	}
			// 	else {
			// 		document.getElementById("customer_comeback_per_up").innerHTML = `<i class="fa fa-arrow-up"></i> ` + ((result.customersCb - result.customersCbEx) / result.customersCbEx * 100).toFixed(0) + " %";
			// 		document.getElementById("average_earnings_per_up").innerHTML = `<i class="fa fa-arrow-up"></i> ` + ((result.customersCb - result.customersCbEx) / result.customersCbEx * 100).toFixed(0) + " %";
			// 	}
			// 	$("#customer_comeback_per_up").show();
			// 	$("#customer_comeback_per_down").hide();
			// 	document.getElementById("average_earnings_day").innerHTML = parseInt(get_list_date(start, end).length) + " ";
				$("#average_earnings_per_up").show();
				$("#average_earnings_per_down").hide();
			};

			// $("#new_customer_load").hide();
			// $("#new_customer_percent_load").hide();
			// $("#new_customer").show();
			// $("#new_customer_percent").show();
			// document.getElementById("new_customer").innerHTML = result.newCustomers;
			// if (result.customers != 0) {
			// 	document.getElementById("new_customer_percent").innerHTML = (result.newCustomers / result.customers * 100).toFixed(0) + '%';
			// } else {
			// 	document.getElementById("new_customer_percent").innerHTML = '0%';
			// };
			// document.getElementById("new_customer_day").innerHTML = parseInt(get_list_date(start, end).length) + " ";
			// $("#new_customer_avg_load").hide();
			// $("#new_customer_avg").show();
			// document.getElementById("new_customer_avg").innerHTML = parseInt(result.newCustomers / get_list_date(start, end).length);
			// if (result.newCustomersEx > result.newCustomers) {
			// 	if (result.newCustomers == 0) {
			// 		document.getElementById("new_customer_per_down").innerHTML = `<i class="fa fa-arrow-down"></i> ` + 100 + " %";
			// 	}
			// 	else {
			// 		document.getElementById("new_customer_per_down").innerHTML = `<i class="fa fa-arrow-down"></i> ` + ((result.newCustomersEx - result.newCustomers) / result.newCustomersEx * 100).toFixed(0) + " %";
			// 	}
			// 	$("#new_customer_per_down").show();
			// 	$("#new_customer_per_up").hide();
			// }
			// else {
			// 	if (result.newCustomersEx == 0) {
			// 		document.getElementById("new_customer_per_up").innerHTML = `<i class="fa fa-arrow-up"></i> ` + 100 + " %";
			// 	}
			// 	else {
			// 		document.getElementById("new_customer_per_up").innerHTML = `<i class="fa fa-arrow-up"></i> ` + ((result.newCustomers - result.newCustomersEx) / result.newCustomersEx * 100).toFixed(0) + " %";
			// 	}
			// 	$("#new_customer_per_up").show();
			// 	$("#new_customer_per_down").hide();
			// };

			// $("#avpv_load").hide();
			// if (result.customers != 0) {
			// 	document.getElementById("avpv").innerHTML = (result.totalVisits / result.customers).toFixed(0);
			// } else {
			// 	document.getElementById("avpv").innerHTML = 0;
			// }
			// $("#avpv").show();
			// $("#average_earnings_load").hide();
			// $("#average_earnings").show();
			// document.getElementById("average_earnings").innerHTML = (result.customersCb * average_earnings).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
			// $("#average_earnings_avg_load").hide();
			// $("#average_earnings_avg").show();
			// document.getElementById("average_earnings_avg").innerHTML = parseInt(result.customersCb * average_earnings / get_list_date(start, end).length).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");

			var arr_customer = [];
			arr_customer.push(newCustomers);
			arr_customer.push(customersCb);
			var labes_arr = [ngettext("Khach_hang_moi"), ngettext("Khach_hang_quay_lai")];
			update_chart(customers_chart, labes_arr, arr_customer)
			$("#customers_load").hide();
			$("#customers").show();
		})
	};
	cus_comback();


	//---- nguồn khách hàng

	var data_source = `query{
			resource(merchantId:"`+ String(merchant_id) + `" , dateStart: ` + date_start + `, dateEnd: ` + date_end + `)
			{
				wifi
				chatbot
				pos
				other
			  }
			}`
	if (shop_id != "all") {
		var data_source = `query{
				resource(shopId:"`+ String(shop_id) + `" , dateStart: ` + date_start + `, dateEnd: ` + date_end + `)
				{
					wifi
					chatbot
					pos
					other
				  }
				}`
	}
	async function cus_source() {
		await fetch('https://report.nextify.vn/graphql', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Accept': 'application/json',
			},
			body: JSON.stringify({ query: data_source })
		}).then(r => { return r.json() }).then(data_res => {
			var data_resp = data_res.data.resource;
			var data_arr = ["POS", "WIFI", "CHATBOT", "OTHER"];
			var labes_arr = [data_resp.pos,
			data_resp.wifi,
			data_resp.chatbot,
			data_resp.other
			];

			update_chart(source_customer_chart, data_arr, labes_arr)

		})
	};
	cus_source();


	// coupon đã đổi - đã tạo

	var coupon_redeemed = `query{
			coupon(merchantId:"`+ String(merchant_id) + `", dateStart:` + date_start + `,dateEnd:` + date_end + ` )
			{
				created
				redeemed
			  }
			}`
	if (shop_id != "all") {
		var coupon_redeemed = `query{
				coupon(shopId:"`+ String(shop_id) + `", dateStart:` + date_start + `,dateEnd:` + date_end + ` )
				{
					created
					redeemed
				  }
				}`
	};
	async function coupon() {
		await fetch('https://report.nextify.vn/graphql', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Accept': 'application/json',
			},
			body: JSON.stringify({ query: coupon_redeemed })
		}).then(r => { return r.json() }).then(data => {
			var result = data.data.coupon;
			$("#coupon_redeemed_load").hide();
			$("#coupon_redeemed").show();
			$("#coupon_redeem").show();
			document.getElementById("coupon_redeemed").innerHTML = result.created + "/";
			document.getElementById("coupon_redeem").innerHTML = result.redeemed;
			$("#coupon_redeem_avg_load").hide();
			$("#coupon_redeem_avg").show();
			$("#coupon_redeemed_avg").show();
			document.getElementById("coupon_redeemed_avg").innerHTML = parseInt(result.created / get_list_date(start, end).length);
			document.getElementById("coupon_redeem_avg").innerHTML = parseInt(result.redeemed / get_list_date(start, end).length);
		})
	};
	coupon();


	//  số lượt tin nhắn đã gửi 

	if (shop_id != "all") {
		var data_sms = `query{
			sendlog(shopId:"`+ String(shop_id) + `", dateStart:` + date_start + `, dateEnd:` + date_end + `)
			{
				sms
				email
				zalo
				chatbot
			  }
			}`
	}
	else {
		var data_sms = `query{
			sendlog(merchantId:"`+ String(merchant_id) + `", dateStart:` + date_start + `, dateEnd:` + date_end + `)
			{
				sms
				email
				zalo
				chatbot
			  }
			}`
	};
	async function send_log() {
		await fetch('https://report.nextify.vn/graphql', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Accept': 'application/json',
			},
			body: JSON.stringify({ query: data_sms })
		}).then(r => { return r.json() }).then(data_res => {
			var data_resp = data_res.data.sendlog;
			var labes_arr = ["SMS", "ZALO", "EMAIL", "CHATBOT"];
			if (data_resp.length != 0) {
				var data_arr = [data_resp.sms, data_resp.zalo, data_resp.email, data_resp.chatbot];
				update_chart(sms_sent, labes_arr, data_arr)
			}
		})
	};
	send_log();

	// khách theo khung giờ 

	var data_hours = `query{
			request(merchantId:"`+ String(merchant_id) + `", listDate: [` + get_list_date(start, end) + `])
			{
				hourCustomers{
					percent
					typeHours
				}
				
			}
		}`
	if (shop_id != "all") {

		var data_hours = `query{
				requestshop(shopId:"`+ String(shop_id) + `", listDate: [` + get_list_date(start, end) + `])
				{
					hourCustomers{
						percent
						typeHours
					}
					
				}
			}`;
		async function cus_hour() {
			await fetch('https://report.nextify.vn/graphql', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'Accept': 'application/json',
				},
				body: JSON.stringify({ query: data_hours })
			}).then(r => { return r.json() }).then(data_res => {
				var data_resp = data_res.data.requestshop;
				var labes_arr = ["08:00 - 10:59", "11:00 - 13:59", "14:00 - 17:59", "18:00 - 20:59", "21:00 - 23:59", "00:00 - 07:59"];
				var data_8 = [];
				var data_11 = [];
				var data_14 = [];
				var data_18 = [];
				var data_21 = [];
				var data_00 = [];
				var i = 0;
				for (i = 0; i < data_resp.length; i++) {
					var range_item = data_resp[i];
					data_8.push(range_item.hourCustomers[0].percent);
					data_11.push(range_item.hourCustomers[1].percent);
					data_14.push(range_item.hourCustomers[2].percent);
					data_18.push(range_item.hourCustomers[3].percent);
					data_21.push(range_item.hourCustomers[4].percent);
					data_00.push(range_item.hourCustomers[5].percent);
				}

				var data_arr12 = [parseInt((data_8.reduce((a, b) => a + b, 0)).toFixed(2)),
				parseInt((data_11.reduce((a, b) => a + b, 0)).toFixed(2)),
				parseInt((data_14.reduce((a, b) => a + b, 0)).toFixed(2)),
				parseInt((data_18.reduce((a, b) => a + b, 0)).toFixed(2)),
				parseInt((data_21.reduce((a, b) => a + b, 0)).toFixed(2)),
				parseInt((data_00.reduce((a, b) => a + b, 0)).toFixed(2)),];
				var average = data_arr12.reduce((a, b) => a + b, 0);
				if (average === 0) {
					update_chart(visit_by_hour_chart, labes_arr, data_arr12)
				}
				else {
					var data_arr = [(data_arr12[0] / average * 100).toFixed(0),
					(data_arr12[1] / average * 100).toFixed(0),
					(data_arr12[2] / average * 100).toFixed(0),
					(data_arr12[3] / average * 100).toFixed(0),
					(data_arr12[4] / average * 100).toFixed(0)];
					data_arr.push(100 - (parseInt(data_arr[0]) + parseInt(data_arr[1]) + parseInt(data_arr[2]) + parseInt(data_arr[3]) + parseInt(data_arr[4])))
					update_chart(visit_by_hour_chart, labes_arr, data_arr)
				}
			})
		};
		cus_hour();
	}
	else {
		async function cus_hour() {
			await fetch('https://report.nextify.vn/graphql', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'Accept': 'application/json',
				},
				body: JSON.stringify({ query: data_hours })
			}).then(r => { return r.json() }).then(data_res => {
				var data_resp = data_res.data.request;
				var labes_arr = ["08:00 - 10:59", "11:00 - 13:59", "14:00 - 17:59", "18:00 - 20:59", "21:00 - 23:59", "00:00 - 07:59"];
				var data_8 = [];
				var data_11 = [];
				var data_14 = [];
				var data_18 = [];
				var data_21 = [];
				var data_00 = [];
				var i = 0;
				for (i = 0; i < data_resp.length; i++) {
					var range_item = data_resp[i];
					data_8.push(range_item.hourCustomers[0].percent);
					data_11.push(range_item.hourCustomers[1].percent);
					data_14.push(range_item.hourCustomers[2].percent);
					data_18.push(range_item.hourCustomers[3].percent);
					data_21.push(range_item.hourCustomers[4].percent);
					data_00.push(range_item.hourCustomers[5].percent);
				}

				var data_arr12 = [parseInt((data_8.reduce((a, b) => a + b, 0)).toFixed(2)),
				parseInt((data_11.reduce((a, b) => a + b, 0)).toFixed(2)),
				parseInt((data_14.reduce((a, b) => a + b, 0)).toFixed(2)),
				parseInt((data_18.reduce((a, b) => a + b, 0)).toFixed(2)),
				parseInt((data_21.reduce((a, b) => a + b, 0)).toFixed(2)),
				parseInt((data_00.reduce((a, b) => a + b, 0)).toFixed(2)),];
				var average = data_arr12.reduce((a, b) => a + b, 0);
				if (average === 0) {
					update_chart(visit_by_hour_chart, labes_arr, data_arr12)
				}
				else {
					var data_arr = [(data_arr12[0] / average * 100).toFixed(0),
					(data_arr12[1] / average * 100).toFixed(0),
					(data_arr12[2] / average * 100).toFixed(0),
					(data_arr12[3] / average * 100).toFixed(0),
					(data_arr12[4] / average * 100).toFixed(0)];
					data_arr.push(100 - (parseInt(data_arr[0]) + parseInt(data_arr[1]) + parseInt(data_arr[2]) + parseInt(data_arr[3]) + parseInt(data_arr[4])))
					update_chart(visit_by_hour_chart, labes_arr, data_arr)
				}
			});

		};
		cus_hour();
	};
	// Top khách hàng


	// khách hàng theo thiết bị

	var data_devices = `query{
			request(merchantId:"`+ String(merchant_id) + `", listDate: [` + get_list_date(start, end) + `])
			{
				deviceCustomers{
					typeDevice
					count
				  }
				
			}
		}`
	if (shop_id != "all") {
		var data_devices = `query{
				requestshop(shopId:"`+ String(shop_id) + `", listDate: [` + get_list_date(start, end) + `])
				{
					deviceCustomers{
						typeDevice
						count
					  }
					
				}
			}`;
		async function cus_device() {
			await fetch('https://report.nextify.vn/graphql', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'Accept': 'application/json',
				},
				body: JSON.stringify({ query: data_devices })
			}).then(r => { return r.json() }).then(data_res => {
				var data_resp = data_res.data.requestshop;
				var labes_arr = ["Ios", "Mac OS", "Android", "Windows", "Linux", "Other"];
				var data_ios = [];
				var data_mac = [];
				var data_and = [];
				var data_win = [];
				var data_lin = [];
				var data_oth = [];
				var i = 0;
				for (i = 0; i < data_resp.length; i++) {
					var range_item = data_resp[i];
					data_ios.push(range_item.deviceCustomers[0].count);
					data_mac.push(range_item.deviceCustomers[1].count);
					data_and.push(range_item.deviceCustomers[2].count);
					data_win.push(range_item.deviceCustomers[3].count);
					data_lin.push(range_item.deviceCustomers[4].count);
					data_oth.push(range_item.deviceCustomers[5].count);
				}
				var data_arr = [data_ios.reduce((a, b) => a + b, 0),
				data_mac.reduce((a, b) => a + b, 0),
				data_and.reduce((a, b) => a + b, 0),
				data_win.reduce((a, b) => a + b, 0),
				data_lin.reduce((a, b) => a + b, 0),
				data_oth.reduce((a, b) => a + b, 0)];
				update_chart(customer_by_device_chart, labes_arr, data_arr)
			})
		}; cus_device();
	}


	else {
		async function cus_device() {
			await fetch('https://report.nextify.vn/graphql', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'Accept': 'application/json',
				},
				body: JSON.stringify({ query: data_devices })
			}).then(r => { return r.json() }).then(data_res => {
				var data_resp = data_res.data.request;
				var labes_arr = ["Ios", "Mac OS", "Android", "Windows", "Linux", "Other"];
				var data_ios = [];
				var data_mac = [];
				var data_and = [];
				var data_win = [];
				var data_lin = [];
				var data_oth = [];
				var i = 0;
				for (i = 0; i < data_resp.length; i++) {
					var range_item = data_resp[i];
					data_ios.push(range_item.deviceCustomers[0].count);
					data_mac.push(range_item.deviceCustomers[1].count);
					data_and.push(range_item.deviceCustomers[2].count);
					data_win.push(range_item.deviceCustomers[3].count);
					data_lin.push(range_item.deviceCustomers[4].count);
					data_oth.push(range_item.deviceCustomers[5].count);
				}
				var data_arr = [data_ios.reduce((a, b) => a + b, 0),
				data_mac.reduce((a, b) => a + b, 0),
				data_and.reduce((a, b) => a + b, 0),
				data_win.reduce((a, b) => a + b, 0),
				data_lin.reduce((a, b) => a + b, 0),
				data_oth.reduce((a, b) => a + b, 0)];
				update_chart(customer_by_device_chart, labes_arr, data_arr)
			})
		};
		cus_device();
	}

	//----  Churn rate and crr
	//
	// if (shop_id == "all") {
	// 	var query = `query{
	// 		churnrateCrr(merchantId:"`+ String(merchant_id) + `", dateStart: ` + date_start + `, dateEnd: ` + date_end + `)
	// 		{
	// 			churnRate
	// 		    crr
	// 		    avgVisit
	// 		  }
	// 		}`;
	// } else {
	// 	var query = `query{
	// 		churnrateCrr(shopId:"`+ String(shop_id) + `", dateStart: ` + date_start + `, dateEnd: ` + date_end + `)
	// 		{
	// 			churnRate
	// 		    crr
	// 		    avgVisit
	// 		  }
	// 		}`;
	// };
	// async function churnrate_crr() {
	// 	await fetch('https://report.nextify.vn/graphql', {
	// 		method: 'POST',
	// 		headers: {
	// 			'Content-Type': 'application/json',
	// 			'Accept': 'application/json',
	// 		},
	// 		body: JSON.stringify({ query: query })
	// 	}).then(r => { return r.json() }).then(data_lc => {
	// 		var data_lc = data_lc;
	// 		$("#crr_load").hide();
	// 		$("#churnrate_load").hide();
	// 		var churnrate = data_lc.data.churnrateCrr.churnRate;
	// 		var earnings = $("#average_earnings_inp").val();
	// 		if (!earnings || earnings == 'None' || earnings == 'none') {
	// 			earnings = 300000;
	// 		};
	// 		$("#clv_load").hide();
	// 		$("#clv").show();
	// 		if (churnrate == 0) {
	// 			document.getElementById("clv").innerHTML = "<i class='fas fa-infinity' style='font-size: 40px'></i>";
	// 		} else {
	// 			document.getElementById("clv").innerHTML = (data_lc.data.churnrateCrr.avgVisit * earnings / churnrate * 100).toFixed(0).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
	// 		};
	// 		var labes_arr = ["Churn Rate", "Retention Rate"];
	// 		var data_arr = []
	// 		data_arr.push(data_lc.data.churnrateCrr.churnRate);
	// 		data_arr.push(data_lc.data.churnrateCrr.crr);
	// 		update_chart(churnrate_crr_chart, labes_arr, data_arr)
	// 		$("#churnrate_crr").show();
	// 	})
	// };
	// churnrate_crr();

	// khách hàng theo thứ

	var data_customer_by_weekday = `query{
		weekdaycustomer(merchantId:"`+ String(merchant_id) + `", listDay: [` + get_list_date(start, end) + `])
		{
			Monday
			Tuesday
			Wednesday
			Thursday
			Friday
			Saturday
			Sunday
		  }
		}`
	if (shop_id != "all") {
		var data_customer_by_weekday = `query{
			weekdaycustomer(shopId:"`+ String(shop_id) + `", listDay: [` + get_list_date(start, end) + `])
			{
				Monday
				Tuesday
				Wednesday
				Thursday
				Friday
				Saturday
				Sunday
			  }
			}`
	}
	async function cus_week() {
		await fetch('https://report.nextify.vn/graphql', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Accept': 'application/json',
			},
			body: JSON.stringify({ query: data_customer_by_weekday })
		}).then(r => { return r.json() }).then(data_res => {
			var data_resp = data_res.data.weekdaycustomer;
			// var labes_arr = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"];
			var labes_arr = [ngettext("Thu_2"), ngettext("Thu_3"), ngettext("Thu_4"), ngettext("Thu_5"),
				ngettext("Thu_6"), ngettext("Thu_7"), ngettext("Chu_nhat")]
			var data_avg = [
				data_resp.Monday,
				data_resp.Tuesday,
				data_resp.Wednesday,
				data_resp.Thursday,
				data_resp.Friday,
				data_resp.Saturday,
				data_resp.Sunday
			];
			var avg = data_avg.reduce((a, b) => a + b, 0);
			if (avg === 0) {
				update_chart(customer_by_weekday_chart, labes_arr, data_avg)
			}
			else {
				var data_arr = [
					(data_avg[0] / avg * 100).toFixed(0),
					(data_avg[1] / avg * 100).toFixed(0),
					(data_avg[2] / avg * 100).toFixed(0),
					(data_avg[3] / avg * 100).toFixed(0),
					(data_avg[4] / avg * 100).toFixed(0),
					(data_avg[5] / avg * 100).toFixed(0),
					(100 - ((avg - data_avg[6]) / avg * 100)).toFixed(0)];
				update_chart(customer_by_weekday_chart, labes_arr, data_arr)
			}
		})
	};
	cus_week();
}

//------------------

$('#reportrange').daterangepicker({
	startDate: start,
	endDate: end,
	ranges: {
		[ngettext('Hom_nay')]: [moment(), moment()],
		[ngettext('Hom_qua')]: [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
		[ngettext('7_ngay_truoc')]: [moment().subtract(6, 'days'), moment()],
		[ngettext('Thang_truoc')]: [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')],
		[ngettext('Thang_nay')]: [moment().startOf('month'), moment().endOf('month')],
		[ngettext('Tat_ca_thoi_gian')]: [moment.unix(1514739600), moment()]
	}
}, cb);

cb(start, end);

// Khách hàng theo LƯỢT ĐẾN - KHUNG GIỜ
// ------ khung giờ

var visit_by_hour = document.getElementById('visit_by_hour').getContext('2d');
var visit_by_hour_chart = new Chart(visit_by_hour, {
	type: 'horizontalBar',
	data: {
		labels: ["06:00 - 10:59", "11:00 - 13:59", "14:00 - 17:59", "18:00 - 20:59", "21:00 - 23:59", "00:00 - 05:59"],
		datasets: [{
			data: [0, 0, 0, 0, 0, 0],
			backgroundColor: ["#f57a33", "#f57a33", "#f57a33", "#f57a33", "#f57a33", "#f57a33"],

		}]
	},
	options: {
		legend: {
			display: false,
		},
		title: {
			display: false,
			text: 'Visit by hours'
		},
		tooltips: {
			mode: 'index',
			intersect: false
		},
		responsive: true,
		scales: {
			yAxes: [{
				label: ngettext("khung_gio"),
				stacked: true
			}],
			xAxes: [{
				label: ngettext("khach_hang_theo_ti_le_%"),
				stacked: true
			}]

		}
	}
});

//  số lượt tin nhắn đã gửi 
var sms_sent = document.getElementById('sms_sent').getContext('2d');
var sms_sent = new Chart(sms_sent, {
	type: 'bar',
	data: {
		labels: ["SMS", "ZALO", "MESSAGE", "EMAIL"],
		datasets: [{
			data: [0, 0, 0, 0],
			backgroundColor: ["#f57a33", "#f57a33", "#f57a33", "#f57a33"],

		}]
	},
	options: {
		legend: {
			display: false,
		},
		title: {
			display: false,
			text: 'Visit by hours'
		},
		tooltips: {
			mode: 'index',
			intersect: false
		},
		responsive: true,
		scales: {
			yAxes: [{
				stacked: true
			}],
			xAxes: [{
				stacked: true
			}]

		}
	}
});

// đăng ký trang đăng ký - truy cập wifi


//---- tổng khách theo năm

var chart_sales = document.getElementById('chart_sales').getContext('2d');
var chart_sales_chart = new Chart(chart_sales, {
	type: 'line',
	options: {
		scales: {
			yAxes: [{
				gridLines: {
					lineWidth: 1,
					color: "#212529",
					zeroLineColor: "#212529"
				},
				ticks: {
					callback: function (value) {
						if (!(value % 10)) {
							return value;
						}
					}
				}
			}]
		},
		tooltips: {
			callbacks: {
				label: function (item, data) {
					var label = data.datasets[item.datasetIndex].label || '';
					var yLabel = item.yLabel;
					var content = '';
					if (data.datasets.length > 1) {
						content += '<span class="popover-body-label mr-auto">' + label + '</span>';
					}
					content += '<span class="popover-body-value">' + yLabel + '</span>';
					return content;
				}
			}
		}
	},
	data: {
		labels: [],
		datasets: [{
			data: []
		}]
	},
	options: {
		responsive: true,
		scales: {
			xAxes: [{
				stacked: true,
				styling: {
					display: true,
					borderDash: [2, 2],
					drawBorder: true,
				}
			}],
			yAxes: [{
				stacked: true,

			}]
		}
	}
});

// khách theo lượt đến

var customers_by_visit = document.getElementById('customers_by_visit').getContext('2d');
var customers_by_visit_chart = new Chart(customers_by_visit, {
	type: 'horizontalBar',
	data: {
		labels: [],
		datasets: [{
			data: [],
			backgroundColor: ["#f57a33", "#f57a33", "#f57a33", "#f57a33", "#f57a33"],

		}]
	},
	options: {
		legend: {
			display: false,
		},
		responsive: true,
		scales: {
			xAxes: [{
				stacked: true,
			}],
			yAxes: [{
				stacked: true
			}]
		}
	}
});

//---- nguồn khách hàng

var source_customer = document.getElementById('source_customer').getContext('2d');
var source_customer_chart = new Chart(source_customer, {
	type: 'bar',
	data: {
		labels: [],
		datasets: [{
			data: [],
			backgroundColor: ["#f57a33", "#f57a33", "#f57a33", "#f57a33", "#f57a33"],

		}]
	},
	options: {
		title: {
			display: false,
			text: ngettext("Nguon_khach_hang")
		}
	}
});

// khách hàng theo thiết bị

var customer_by_device = document.getElementById('customer_by_device').getContext('2d');
var customer_by_device_chart = new Chart(customer_by_device, {
	type: 'bar',
	options: {
		scales: {
			yAxes: [{
				gridLines: {
					lineWidth: 1,
					color: '#dfe2e6',
					zeroLineColor: '#dfe2e6'
				},
				ticks: {
					callback: function (value) {
						if (!(value % 10)) {
							return value
						}
					}
				}
			}]
		},
		tooltips: {
			callbacks: {
				label: function (item, data) {
					var label = data.datasets[item.datasetIndex].label || '';
					var yLabel = item.yLabel;
					var content = '';
					if (data.datasets.length > 1) {
						content += '<span class="popover-body-label mr-auto">' + label + '</span>';
					}
					content += '<span class="popover-body-value">' + yLabel + '</span>';
					return content;
				}
			}
		}
	},
	data: {
		labels: [],
		datasets: [{
			data: [],
		}]
	}
});

// khách hàng theo thứ
var customer_by_weekday = document.getElementById('customer_by_weekday').getContext('2d');
var customer_by_weekday_chart = new Chart(customer_by_weekday, {
	type: 'bar',
	options: {
		scales: {
			yAxes: [{
				gridLines: {
					lineWidth: 1,
					color: '#dfe2e6',
					zeroLineColor: '#dfe2e6'
				},
				ticks: {
					callback: function (value) {
						if (!(value % 10)) {
							return value
						}
					}
				}
			}]
		},
		tooltips: {
			callbacks: {
				label: function (item, data) {
					var label = data.datasets[item.datasetIndex].label || '';
					var yLabel = item.yLabel;
					var content = '';
					if (data.datasets.length > 1) {
						content += '<span class="popover-body-label mr-auto">' + label + '</span>';
					}
					content += '<span class="popover-body-value">' + yLabel + '</span>';
					return content;
				}
			}
		}
	},
	data: {
		labels: [],
		datasets: [{
			data: [],
		}]
	}
});

// khac hang trung thanh, khach hang roi bo

// var churnrate_crr = document.getElementById('churnrate_crr');
// var churnrate_crr_chart = new Chart(churnrate_crr, {
//     type: 'doughnut',
//     data: {
// 	    labels: [],
// 	    datasets: [
// 	      {
// 	        data: [],
// 	        backgroundColor: [
// 				"#2c7be5",
// 				"#d2ddec"
// 	        ],
// 	        borderColor: [
// 				"#E9DAC6",
// 				"#CBCBCB"
// 	        ],
// 	        borderWidth: [1, 1]
// 	      }
// 	    ]
// 	},
// 	options: {
// 	    responsive: true,
// 	    title: {
// 			display: true,
// 			position: "top",
// 			fontSize: 18,
// 			fontColor: "#111"
// 	    },
// 	    legend: {
// 			display: false,
// 			position: "bottom",
// 			labels: {
// 				fontColor: "#333",
// 				fontSize: 16
// 			}
// 	    },
// 	    tooltips: {
// 	      	callbacks: {
// 		        label: function(tooltipItem, data) {
// 					var dataset = data.datasets[tooltipItem.datasetIndex];
// 					var total = dataset.data.reduce(function(previousValue, currentValue, currentIndex, array) {
// 						return previousValue + currentValue;
// 					});
// 					var currentValue = dataset.data[tooltipItem.index];
// 					var percentage = Math.floor(((currentValue/total) * 100)+0.5);
// 					return percentage + "%";
// 		        }
// 			}
//     	}
// 	}
// });


// lien he thu thap duoc

var contacts_collect = document.getElementById('contacts_collect');
var contacts_collect_chart = new Chart(contacts_collect, {
    type: 'doughnut',
    data: {
	    labels: [],
	    datasets: [
	      {
	        data: [],
	        backgroundColor: [
				"#2c7be5",
				"#d2ddec"
	        ],
	        borderColor: [
				"#E9DAC6",
				"#CBCBCB"
	        ],
	        borderWidth: [1, 1]
	      }
	    ]
	},
	options: {
	    responsive: true,
	    title: {
			display: true,
			position: "top",
			fontSize: 18,
			fontColor: "#111"
	    },
	    legend: {
			display: false,
			position: "bottom",
			labels: {
				fontColor: "#333",
				fontSize: 16
			}
	    },
	    tooltips: {
	      	callbacks: {
		        label: function(tooltipItem, data) {
					var dataset = data.datasets[tooltipItem.datasetIndex];
					var total = dataset.data.reduce(function(previousValue, currentValue, currentIndex, array) {
						return previousValue + currentValue;
					});
					var currentValue = dataset.data[tooltipItem.index];
					var percentage = Math.floor(((currentValue/total) * 100)+0.5);
					return percentage + "%";
		        }
			}
    	}
	}
});

// cross shopers

var cross_shopers = document.getElementById('cross_shopers');
var cross_shopers_chart = new Chart(cross_shopers, {
    type: 'doughnut',
    data: {
	    labels: [],
	    datasets: [
	      {
	        data: [],
	        backgroundColor: [
				"#2c7be5",
				"#d2ddec"
	        ],
	        borderColor: [
				"#E9DAC6",
				"#CBCBCB"
	        ],
	        borderWidth: [1, 1]
	      }
	    ]
	},
	options: {
	    responsive: true,
	    title: {
			display: true,
			position: "top",
			fontSize: 18,
			fontColor: "#111"
	    },
	    legend: {
			display: false,
			position: "bottom",
			labels: {
				fontColor: "#333",
				fontSize: 16
			}
	    },
	    tooltips: {
	      	callbacks: {
		        label: function(tooltipItem, data) {
					var dataset = data.datasets[tooltipItem.datasetIndex];
					var total = dataset.data.reduce(function(previousValue, currentValue, currentIndex, array) {
						return previousValue + currentValue;
					});
					var currentValue = dataset.data[tooltipItem.index];
					var percentage = Math.floor(((currentValue/total) * 100)+0.5);
					return percentage + "%";
		        }
			}
    	}
	}
});


// customers

var customers = document.getElementById('customers');
var customers_chart = new Chart(customers, {
    type: 'doughnut',
    data: {
	    labels: [],
	    datasets: [
	      {
	        data: [],
	        backgroundColor: [
				"#2c7be5",
				"#d2ddec"
	        ],
	        borderColor: [
				"#E9DAC6",
				"#CBCBCB"
	        ],
	        borderWidth: [1, 1]
	      }
	    ]
	},
	options: {
	    responsive: true,
	    title: {
			display: true,
			position: "top",
			fontSize: 18,
			fontColor: "#111"
	    },
	    legend: {
			display: false,
			position: "bottom",
			labels: {
				fontColor: "#333",
				fontSize: 16
			}
	    },
	    tooltips: {
	      	callbacks: {
		        label: function(tooltipItem, data) {
					var dataset = data.datasets[tooltipItem.datasetIndex];
					var total = dataset.data.reduce(function(previousValue, currentValue, currentIndex, array) {
						return previousValue + currentValue;
					});
					var currentValue = dataset.data[tooltipItem.index];
					var percentage = Math.floor(((currentValue/total) * 100)+0.5);
					return percentage + "%";
		        }
			}
    	}
	}
});