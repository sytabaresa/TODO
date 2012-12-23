$ = jQuery

# ENTRY POINT (jQuery)
# =======================================================================================
$ ->

	appendText = (t) ->
		return ->
			theinput = $("input#finance-input:first")
			theinput.val(theinput.val()+t)
			return false

	$("td#dial0").find("a").click appendText("0")
	$("td#dial1").find("a").click appendText("1")
	$("td#dial2").find("a").click appendText("2")
	$("td#dial3").find("a").click appendText("3")
	$("td#dial4").find("a").click appendText("4")
	$("td#dial5").find("a").click appendText("5")
	$("td#dial6").find("a").click appendText("6")
	$("td#dial7").find("a").click appendText("7")
	$("td#dial8").find("a").click appendText("8")
	$("td#dial9").find("a").click appendText("9")
	$("td#dialdot").find("a").click appendText(".")
	$("td#dialdel").find("a").click ->
		theinput = $("input#finance-input:first")
		previous = theinput.val()
		theinput.val(previous.substr(0,previous.length-1))
		return false

	return false
