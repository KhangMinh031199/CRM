// tooltips

$("#tooltip_click").tooltip({
	"title": "số lượt nhấp chuột vào quảng cáo của bạn, bao gồm tương tác với vùng chứa quảng cáo, liên kết đến trang đích và liên kết đến trải nghiệm quảng cáo mở rộng",
	"animation": true,

});
$("#tooltip_adim").tooltip({
	"title": "số lần quảng cáo của bạn xuất hiện trên màn hình",
	"animation": true,

});
$("#tooltip_egn").tooltip({
	"title": "là số người có tương tác với nội dung quảng cáo của bạn, bao gồm: số người click, bình luận và chia sẻ và những người có xem video hoặc có click vào liên kết hay hình ảnh bạn post lên",
	"animation": true,
});
$("#tooltip_walk").tooltip({
	"title": "là số lượt khách đến sau khi xem quảng cáo từ các nền tảng online (facebook, instagram)",
	"animation": true,
});


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
var merchant_id = $("#merchant_id").val();
var campaign_id_select = $("#campaign_id").val();
// $('#campanign').select2();
var start = moment().subtract(6, 'days');
var end = moment();

// get number day
function getDates(start, end) {
	var dateArray = [];
	var currentDate = moment(start);
	var stopDate = moment(end);
	while (currentDate <= stopDate) {
		dateArray.push(moment(currentDate).format('DD/MM'));
		currentDate = moment(currentDate).add(1, 'days');
	}
	return dateArray.length;
};
function convert_date(label) {
	if (label.length == 1) {
		var day = label[0];
		console.log(day);
		day_1 = moment.unix(new Date(day.split("-").reverse().join("-")).getTime() / 1000 - 86400).format("DD-MM-YYYY");
		day_2 = moment.unix(new Date(day.split("-").reverse().join("-")).getTime() / 1000 + 86400).format("DD-MM-YYYY");
		return [day_1, day, day_2]
	}
	else {
		return label
	}
};

function convert_data(data) {
	if (data.length == 1) {
		return [0, data[0], 0]
	}
	else {
		return data
	}
};
if ($("#created_time_ts").val() != 'None' && $("#created_time_ts").val()) {
	var timestamp = moment.unix($("#created_time_ts").val());
	var start = timestamp;
}
else {
	var start = moment().subtract(1, 'year');
};

if ($("#completed_time_ts").val() && $("#completed_time_ts").val() != 'None') {
	var timestamp = moment.unix($("#completed_time_ts").val());
	var end = timestamp;
}
else {
	var end = moment();
};

var data = "1 năm trước";
function req_data(start, end, data) {
	$('#reportrange span').html(start.format('DD/MM/YYYY') + ' - ' + end.format('DD/MM/YYYY'));
	var created_time_ts = new Date(start.format('MM/DD/YYYY')).getTime() / 1000;
	var completed_time_ts = new Date(end.format('MM/DD/YYYY')).getTime() / 1000;
	if (data) {
		if (merchant_id.length > 0) {
			if (data.includes("Tháng này")) {
				$("#loading").show();
				console.log("Tháng này");
				$.ajax({
					url: "/advertising",
					type: "POST",
					data: {
						'campaign_id': campaign_id_select,
						'completed_time_ts': completed_time_ts,
						'created_time_ts': created_time_ts,
						'merchant_id': merchant_id,
					},
					success: function (res) {
						$("#all").empty();
						$("#all").append(res);
						$("#loading").hide();
					},
					error: function (request, status, error) {
						console.log("ajax call went wrong:" + request.responseText);
					}
				});
			}
			else if (data.includes("30")) {
				$("#loading").show();
				console.log("30 ngày trước");
				$.ajax({
					url: "/advertising",
					type: "POST",
					data: {
						'campaign_id': campaign_id_select,
						'completed_time_ts': completed_time_ts,
						'created_time_ts': created_time_ts,
						'merchant_id': merchant_id,
					},
					success: function (res) {
						$("#all").empty();
						$("#all").append(res);
						$("#loading").hide();
					},
					error: function (request, status, error) {
						console.log("ajax call went wrong:" + request.responseText);
					}
				});
			}
			else if (data.includes("90")) {
				$("#loading").show();
				console.log("90 days");
				$.ajax({
					url: "/advertising",
					type: "POST",
					data: {
						'campaign_id': campaign_id_select,
						'completed_time_ts': completed_time_ts,
						'created_time_ts': created_time_ts,
						'merchant_id': merchant_id,
					},
					success: function (res) {
						$("#all").empty();
						$("#all").append(res);
						$("#loading").hide();
					},
					error: function (request, status, error) {
						console.log("ajax call went wrong:" + request.responseText);
					}
				});
			}
			else if (data.includes("1")) {
				$("#loading").show();
				console.log("1 year ago");
				$.ajax({
					url: "/advertising",
					type: "POST",
					data: {
						'campaign_id': campaign_id_select,
						'completed_time_ts': completed_time_ts,
						'created_time_ts': created_time_ts,
						'merchant_id': merchant_id,
					},
					success: function (res) {
						$("#all").empty();
						$("#all").append(res);
						$("#loading").hide();
					},
					error: function (request, status, error) {
						console.log("ajax call went wrong:" + request.responseText);
					}
				});
			}
			else {
				$("#loading").show();
				console.log("all time");
				$('#reportrange span').html('Tất cả thời gian');
				$.ajax({
					url: "/advertising",
					type: "POST",
					data: {
						'campaign_id': campaign_id_select,
						'merchant_id': merchant_id,
					},
					success: function (res) {
						$("#all").empty();
						$("#all").append(res);
						var label = ["0", "0", "0", "0", "0", "0"];
						var data = [0, 0, 0, 0, 0, 0];
						update_chart(walk_add_click_chart, label, data);
						$('#reportrange span').html('Tất cả thời gian');
						$("#loading").hide();
					},
					error: function (request, status, error) {
						console.log("ajax call went wrong:" + request.responseText);
					}
				});
			}

		}

	}
}



// UPDATE CHART

function update_chart(chart, label, data) {
	chart.data.labels = label;
	chart.data.datasets[0].data = data;
	chart.update();
};

// CLICK
$("#platform").click(function () {
	$("#data_imps").hide();
	$("#data_clicks").hide();
	$("#data_enga").hide();
	$("#platform_detail").show();
	document.getElementById('platform').className = 'tabs-unstyled-tab active';
	document.getElementById('analysis').className = 'tabs-unstyled-tab';

});
if (merchant_id.length <= 0) {
	var campaign_info_detail = JSON.parse($("#campaign_info_detail").val());
	$("#walk_throughs").click(function () {
		var label = [0, 0, 0, 0, 0, 0];
		var data = [0, 0, 0, 0, 0, 0];
		update_chart(walk_add_click_chart, label, data);
		document.getElementById('walk_throughs').className = 'tabs-unstyled-tab active';
		document.getElementById('add_impressions').className = 'tabs-unstyled-tab';
		document.getElementById('enga').className = 'tabs-unstyled-tab';
		document.getElementById('clicks').className = 'tabs-unstyled-tab';
		document.getElementById('walk_add_click_total').innerHTML = '0';
		document.getElementById('analysis').className = 'tabs-unstyled-tab active';
		document.getElementById('platform').className = 'tabs-unstyled-tab';
	});
	$("#add_impressions").click(function () {
		$("#walk_add_click_load").show();
		var label = [];
		var data = [];
		for (i = 0; i < campaign_info_detail.impressions.date.length; i++) {
			label.push(campaign_info_detail.impressions.date[i].date);
			data.push(campaign_info_detail.impressions.date[i].value);
		};
		$("#walk_add_click_load").hide();
		update_chart(walk_add_click_chart, convert_date(label), convert_data(data));
		document.getElementById('walk_throughs').className = 'tabs-unstyled-tab';
		document.getElementById('add_impressions').className = 'tabs-unstyled-tab active';
		document.getElementById('enga').className = 'tabs-unstyled-tab';
		document.getElementById('clicks').className = 'tabs-unstyled-tab';
		document.getElementById('analysis').className = 'tabs-unstyled-tab active';
		document.getElementById('platform').className = 'tabs-unstyled-tab';
		document.getElementById('walk_add_click_total').innerHTML = $("#impressions_total_detail").val();
		$("#data_imps").show();
		$("#data_clicks").hide();
		$("#data_enga").hide();
		$("#platform_detail").hide();

	})
	$("#enga").click(function () {
		var label = [];
		var data = [];
		for (i = 0; i < campaign_info_detail.post_engagement.date.length; i++) {
			label.push(campaign_info_detail.post_engagement.date[i].date);
			data.push(campaign_info_detail.post_engagement.date[i].value);
		}
		update_chart(walk_add_click_chart, convert_date(label), convert_data(data));
		document.getElementById('walk_throughs').className = 'tabs-unstyled-tab';
		document.getElementById('add_impressions').className = 'tabs-unstyled-tab';
		document.getElementById('enga').className = 'tabs-unstyled-tab active';
		document.getElementById('clicks').className = 'tabs-unstyled-tab';
		document.getElementById('analysis').className = 'tabs-unstyled-tab active';
		document.getElementById('platform').className = 'tabs-unstyled-tab';
		document.getElementById('walk_add_click_total').innerHTML = $("#post_engagement_total_detail").val();
		$("#data_imps").hide();
		$("#data_clicks").hide();
		$("#data_enga").show();
		$("#platform_detail").hide();

	})
	$("#clicks").click(function () {
		var label = [];
		var data = [];
		for (i = 0; i < campaign_info_detail.clicks.date.length; i++) {
			label.push(campaign_info_detail.clicks.date[i].date);
			data.push(campaign_info_detail.clicks.date[i].value);
		}
		update_chart(walk_add_click_chart, convert_date(label), convert_data(data));
		document.getElementById('clicks').className = 'tabs-unstyled-tab active';
		document.getElementById('walk_throughs').className = 'tabs-unstyled-tab';
		document.getElementById('add_impressions').className = 'tabs-unstyled-tab';
		document.getElementById('enga').className = 'tabs-unstyled-tab';
		document.getElementById('analysis').className = 'tabs-unstyled-tab active';
		document.getElementById('platform').className = 'tabs-unstyled-tab';
		document.getElementById('walk_add_click_total').innerHTML = $("#clicks_total_detail").val();
		$("#data_imps").hide();
		$("#data_clicks").show();
		$("#data_enga").hide();
		$("#platform_detail").hide();

	})

	$("#analysis").click(function () {
		$("#walk_add_click_load").show();
		var label = [];
		var data = [];
		for (i = 0; i < campaign_info_detail.impressions.date.length; i++) {
			label.push(campaign_info_detail.impressions.date[i].date);
			data.push(campaign_info_detail.impressions.date[i].value);
		}
		$("#walk_add_click_load").hide();
		update_chart(walk_add_click_chart, convert_date(label), convert_data(data));
		document.getElementById('walk_throughs').className = 'tabs-unstyled-tab';
		document.getElementById('add_impressions').className = 'tabs-unstyled-tab active';
		document.getElementById('enga').className = 'tabs-unstyled-tab';
		document.getElementById('clicks').className = 'tabs-unstyled-tab';
		document.getElementById('analysis').className = 'tabs-unstyled-tab active';
		document.getElementById('platform').className = 'tabs-unstyled-tab';
		document.getElementById('walk_add_click_total').innerHTML = $("#impressions_total_detail").val();
		$("#data_imps").show();
		$("#data_clicks").hide();
		$("#data_enga").hide();
		$("#platform_detail").hide();

	});
};
if (merchant_id.length > 0) {
	if ($("#data_chart").val().length > 0) {
		var data_chart = JSON.parse($("#data_chart").val());
		console.log(merchant_id);
		var label_all = [];
		var data_imps_all = [];
		var data_enga_all = [];
		var data_clicks_all = [];
		for (i = 0; i < data_chart.insights_all_ads.length; i++) {

			label_all.push(data_chart.insights_all_ads[i].date);
			data_imps_all.push(data_chart.insights_all_ads[i].impressions);
			data_enga_all.push(data_chart.insights_all_ads[i].post_engagement);
			data_clicks_all.push(data_chart.insights_all_ads[i].clicks);

		};

		$("#add_impressions").click(function () {
			$("#walk_add_click_load").show();
			$("#walk_add_click_load").hide();
			update_chart(walk_add_click_chart, convert_date(label_all), convert_data(data_imps_all));
			document.getElementById('walk_throughs').className = 'tabs-unstyled-tab';
			document.getElementById('add_impressions').className = 'tabs-unstyled-tab active';
			document.getElementById('enga').className = 'tabs-unstyled-tab';
			document.getElementById('clicks').className = 'tabs-unstyled-tab';
			document.getElementById('walk_add_click_total').innerHTML = $("#impressions").val();

		});
		$("#enga").click(function () {

			update_chart(walk_add_click_chart, convert_date(label_all), convert_data(data_enga_all));
			document.getElementById('walk_throughs').className = 'tabs-unstyled-tab';
			document.getElementById('add_impressions').className = 'tabs-unstyled-tab';
			document.getElementById('enga').className = 'tabs-unstyled-tab active';
			document.getElementById('clicks').className = 'tabs-unstyled-tab';
			document.getElementById('walk_add_click_total').innerHTML = $("#post_engagement_total").val();
			$("#data_imps").hide();
			$("#data_clicks").hide();
			$("#data_enga").show();


		});
		$("#walk_throughs").click(function () {

			update_chart(walk_add_click_chart, convert_date([0, 0, 0, 0, 0, 0,]), convert_data([0, 0, 0, 0, 0, 0]));
			document.getElementById('walk_throughs').className = 'tabs-unstyled-tab active';
			document.getElementById('add_impressions').className = 'tabs-unstyled-tab';
			document.getElementById('enga').className = 'tabs-unstyled-tab';
			document.getElementById('clicks').className = 'tabs-unstyled-tab';
			document.getElementById('walk_add_click_total').innerHTML = '0';
		});
		$("#clicks").click(function () {

			update_chart(walk_add_click_chart, convert_date(label_all), convert_data(data_clicks_all));
			document.getElementById('clicks').className = 'tabs-unstyled-tab active';
			document.getElementById('walk_throughs').className = 'tabs-unstyled-tab';
			document.getElementById('add_impressions').className = 'tabs-unstyled-tab';
			document.getElementById('enga').className = 'tabs-unstyled-tab';
			document.getElementById('walk_add_click_total').innerHTML = $("#clicks_total").val();
			$("#data_imps").hide();
			$("#data_clicks").show();
			$("#data_enga").hide();

		});
	}
}


$('#reportrange').daterangepicker({
	startDate: start,
	endDate: end,
	ranges: {
		'Tháng này': [moment().startOf('month'), moment().endOf('month')],
		'30 ngày trước': [moment().subtract(29, 'days'), moment()],
		'90 ngày trước': [moment().subtract(89, 'days'), moment()],
		'1 năm trước': [moment().subtract(1, 'year'), moment()],
		'Tất cả thời gian': [moment.unix(1514739600), moment()]
	}
}, req_data);

req_data(start, end);
var walk_add_click = document.getElementById('walk_add_click').getContext('2d');
var walk_add_click_chart = new Chart(walk_add_click, {
	type: 'line',
	options: {
		scales: {
			yAxes: [{
				gridLines: {
					lineWidth: 1,
					color: Charts.colors.gray[900],
					zeroLineColor: Charts.colors.gray[900]
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
		labels: [0, 0, 0, 0, 0, 0],
		datasets: [{
			data: [0, 0, 0, 0, 0, 0]
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