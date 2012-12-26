$ = jQuery

# ENTRY POINT (jQuery)
# =======================================================================================
$ ->

	initFastButtons()

	# DIALER
	# ==========================================================
	appendText = (t) ->
		return ->
			theinput = $("input#bill-input:first")
			theinput.val(theinput.val()+t)
			return false

	for num in [0..9]
		$("td#dial"+String(num)).find("span").click appendText(String(num))

	$("td#dialdot").find("span").click appendText(".")

	$("td#dialdel").find("span").click ->
		theinput = $("input#bill-input:first")
		previous = theinput.val()
		theinput.val(previous.substr(0,previous.length-1))
		return false

	# Bill form POST send
	# =========================================================
	$("#save-bill").click ->
		# Prepend -/+ sign
		sign = $("div#minus-plus").find("button.active").text()
		money = $("input[name=bill-money]").val()
		$("input[name=bill-money]").val(sign+money)
		# Get method from btn-group radio
		$("input[name=bill-method]").val( $("#bill-method").find("button.active").text().trim() )


	return false
