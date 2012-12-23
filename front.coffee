$ = jQuery

# ENTRY POINT (jQuery)
# =======================================================================================
$ ->

	appendText = (t) ->
		return ->
			theinput = $("input#finance-input:first")
			theinput.val(theinput.val()+t)
			return false

	$("td#dial0").find("span").click appendText("0")
	$("td#dial1").find("span").click appendText("1")
	$("td#dial2").find("span").click appendText("2")
	$("td#dial3").find("span").click appendText("3")
	$("td#dial4").find("span").click appendText("4")
	$("td#dial5").find("span").click appendText("5")
	$("td#dial6").find("span").click appendText("6")
	$("td#dial7").find("span").click appendText("7")
	$("td#dial8").find("span").click appendText("8")
	$("td#dial9").find("span").click appendText("9")
	$("td#dialdot").find("span").click appendText(".")
	$("td#dialdel").find("span").click ->
		theinput = $("input#finance-input:first")
		previous = theinput.val()
		theinput.val(previous.substr(0,previous.length-1))
		return false

	return false
