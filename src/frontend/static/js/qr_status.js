// https://github.com/shanealynn/async_flask/blob/master/static/js/application.js

$(document).ready(function(){
    //connect to the socket server.
    var session_id_var = document.getElementById("session_id").dataset.session_id_data;
    var base_url_var = document.getElementById("base_url").dataset.base_url_data;
    var socket = io.connect(base_url);
    //var socket = io.connect("192.168.1.154:3410");
    var user_1_ready = false;
    var user_2_ready = false;
    var like_string_1;
    var like_string_2;
    var user_1_name;
    var user_2_name

    $('#session_id').html("<h2>" + "session id: " + session_id_var + "</h2>");
    $('#base_url').html("<h2>" + "address: " + base_url_var + "</h2>");


    // TODO: Filter async messages on session id

    // Update page to reflect scanning of qr-code
    socket.on('qr-scanned', function(msg) {
        console.log("Received " + msg.user_id);

        if (msg.session_id == session_id_var) {

            if (msg.user_id == "1") {
                var scanned_qr_1 = document.getElementById("scanned_qr_1").dataset.scanned_qr_1;
                var qr = document.getElementById("qr_1");
                qr.src = scanned_qr_1;
            } 

            if (msg.user_id == "2") {
                var scanned_qr_2 = document.getElementById("scanned_qr_2").dataset.scanned_qr_2;
                var qr = document.getElementById("qr_2");
                qr.src = scanned_qr_2;
            } 
        }  
    
    });

    // Update page to display the user's name
    socket.on('new-user', function(msg) {
        console.log("Received " + msg);

        if (msg.session_id == session_id_var) {

            if (msg.user_id == "1") {
                $('#user_1').html("<h2>" + msg.user_name + "</h2>");
            } 

            if (msg.user_id == "2") {
                $('#user_2').html("<h2>" + msg.user_name + "</h2>");
            } 
        }        
    });

    // Update user state under qr-code
    socket.on('tinder-state', function(msg) {
        console.log("Received " + msg.user_id);

        if (msg.session_id == session_id_var) {

            if (msg.user_id == "1") {
                $('#tinder_state_1').html("<h2>" + msg.tinder_state + "</h2>");
            } 

            if (msg.user_id == "2") {
                $('#tinder_state_2').html("<h2>" + msg.tinder_state + "</h2>");
            } 
        }  
    
    });

    // Redirect QR-page to result page
    socket.on('movie-tinder-end', function(msg) {
        console.log("Received " + msg);

        if (msg.session_id == session_id_var) {

            if (msg.user_id == "1") {
                like_string_1 = msg.like_string
                user_1_ready = true;
                user_1_name =  msg.user_name;
            }

            if (msg.user_id == "2") {
                like_string_2 = msg.like_string
                user_2_ready = true;
                user_2_name =  msg.user_name;
            }

            if (user_1_ready && user_2_ready) {
                window.location = msg.redirect_link + "?" + 
                    "like_string_1=" + like_string_1 + "&" + 
                    "like_string_2=" + like_string_2 + "&" +
                    "user_1=" + user_1_name + "&" +
                    "user_2=" + user_2_name;
            }
        }
    });

});