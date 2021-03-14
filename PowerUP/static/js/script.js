
// ADDING TO BASKET //
function addToBasket(deviceId, URL) {
            $.ajax({
                type: "POST",
                url: URL + deviceId,
                data: $('#addToBasket-btn').serialize(),
                success: function(response) {
                    var json = jQuery.parseJSON(response)
                    document.getElementById('addToBasket-btn-' + deviceId).classList.add("be-green")
                    document.getElementById('addToBasket-btn-' + deviceId).classList.add("be-green.hover")
                    $('#addToBasket-btn-' + deviceId).html(json.f_message)
                    console.log(response);
                },
                error: function(error) {
                	document.getElementById('addToBasket-btn-' + deviceId).classList.add("disabled");
                    document.getElementById('addToBasket-btn-' + deviceId).classList.add("be-gray")
                    $('#addToBasket-btn-' + deviceId).html('Произошла ошибка')
                    console.log(error);
                }
            });
        }




// DELETE FROM BASKET //
function deleteFromBasket(deviceId, URL) {
            $.ajax({
                type: "POST",
                url: URL + deviceId,
                success: function(response) {
                    var json = jQuery.parseJSON(response)
                    console.log(json.status)
                    location.reload()
                },
                error: function(error) {
                    console.log(error)
                }
            });
       }


// SHOW-HIDE PASSWORD IN PROFILE //
function show_hide_password(target, cur_id){
    var input = document.getElementById(cur_id);
    if (input.getAttribute('type') == 'password') {
        target.classList.add('visible');
        input.setAttribute('type', 'text');
    } 
    else {
        target.classList.remove('visible');
        input.setAttribute('type', 'password');
    }
    return false;
}