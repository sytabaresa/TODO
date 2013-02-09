// Generated by CoffeeScript 1.3.3
(function() {
  var $;

  $ = jQuery;

  $(function() {
    var appendText, drawChart, loadData, num, _i;
    if ($("#fastclick").length > 0) {
      initFastButtons();
    }
    appendText = function(t) {
      return function() {
        var theinput;
        theinput = $("input#bill-input:first");
        theinput.val(theinput.val() + t);
        return false;
      };
    };
    for (num = _i = 0; _i <= 9; num = ++_i) {
      $("td#dial" + String(num)).find("span").click(appendText(String(num)));
    }
    $("td#dialdot").find("span").click(appendText("."));
    $("td#dialdel").find("span").click(function() {
      var previous, theinput;
      theinput = $("input#bill-input:first");
      previous = theinput.val();
      theinput.val(previous.substr(0, previous.length - 1));
      return false;
    });
    $("#save-bill").click(function() {
      var money, sign;
      sign = $("div#minus-plus").find("button.active").text();
      money = $("input[name=bill-money]").val();
      $("input[name=bill-money]").val(sign + money);
      return $("input[name=bill-method]").val($("#bill-method").find("button.active").text().trim());
    });
    drawChart = function(data) {
      var chart, chartData, formatter, options;
      chartData = data;
      chartData.unshift(['Category', 'Total expenses']);
      chartData = google.visualization.arrayToDataTable(chartData);
      formatter = new google.visualization.NumberFormat({
        suffix: ' EUR',
        fractionDigits: 2
      });
      formatter.format(chartData, 1);
      options = {};
      $("#chart").html("");
      chart = new google.visualization.PieChart(document.getElementById('chart'));
      return chart.draw(chartData, options);
    };
    loadData = function() {
      var category, row, _j, _len, _results;
      drawChart(expenses);
      expenses.shift(0);
      _results = [];
      for (_j = 0, _len = expenses.length; _j < _len; _j++) {
        category = expenses[_j];
        row = "<tr><td>" + category[0] + "</td><td>" + category[1] + "€</td></td>";
        _results.push($("#expenses-table").append(row));
      }
      return _results;
    };
    if ($("body.statistics").length > 0) {
      google.setOnLoadCallback(loadData);
    }
    return false;
  });

}).call(this);
