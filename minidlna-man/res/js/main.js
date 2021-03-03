
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function flashyFlash() {
  // posted = $("#message").val();
  $("#info").html(
    jQuery("<div/>", {
      id: "msg",
      class: "block w50 center",
      text: "Restart successful ... ",
    })
  )
    .fadeIn('slow').delay(1000).fadeOut()
    .fadeIn('slow').delay(1000).fadeOut()
    .fadeIn('slow').delay(1000).fadeOut();
  console.log("here");
  // e.preventDefault();
}

function reverse(s) {
  return s.split("").reverse().join("");
}

var loaderCharArray = "-\\|/-|"
function poorManLoader(loChAr, _idx) {
  if (_idx == loChAr.length) {
    _idx = 0
  }
  _loaderChar = loChAr[_idx]
  _idx++
  return { loaderChar: _loaderChar, idx: _idx }
}

function poorManLoaderCw(_idx) {
  return poorManLoader(loaderCharArray, loaderIdx)
}

function poorManLoaderCcw(_idx) {
  reversedLoaChaAr = reverse(loaderCharArray)
  return poorManLoader(reversedLoaChaAr, loaderIdx)
}

var stopBeforesendLoader = false

async function beforeSendLoader() {
  stopBeforesendLoader = false
  // var _loaderChar, _loaderIdx = null
  originValue = $("#but").val()

  loaderIdx = 0
  for (let i = 0; i < 24; i++) {
    if (stopBeforesendLoader)
      break;
    loaderCwObj = poorManLoaderCw(loaderIdx)
    loaderCcwObj = poorManLoaderCcw(loaderIdx)
    $("#but").val(`${loaderCcwObj.loaderChar} ${originValue} ${loaderCwObj.loaderChar}`)
    loaderIdx = loaderCwObj.idx
    await sleep(250);
  }
  $("#but").val(originValue)
}

function getInfo(id_number) {
  $.ajax({
    type: "GET",
    beforeSend: beforeSendLoader,
    url: "/restart",
    success: function (response) {
      stopBeforesendLoader = true
      flashyFlash();
    }
  });
};