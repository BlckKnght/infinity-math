// script.js

function a_changed() {
    switch(this.value) {
        case "attack":
            $(".a_weapon").removeClass("hidden");
            $(".d_defense").removeClass("hidden");
            break;
        case "dodge":
            // fallthrough
        case "hack":
            $(".a_weapon").addClass("hidden");
            $(".d_defense").addClass("hidden");
            break;
    }
}

function d_changed() {
    switch(this.value) {
        case "nothing":
            $(".d_target").addClass("hidden");
            $(".d_weapon").addClass("hidden");
            $(".a_defense").addClass("hidden");
            break;
        case "attack":
            $(".d_target").removeClass("hidden");
            $(".d_weapon").removeClass("hidden");
            $(".a_defense").removeClass("hidden");
            break;
        case "dodge":
            // fallthrough
        case "hack":
            $(".d_target").removeClass("hidden");
            $(".d_weapon").addClass("hidden");
            $(".a_defense").addClass("hidden");
            break;
    }
}

$(document).ready(function() {
    $("#a_action_select").change(a_changed).change()
    $("#d_action_select").change(d_changed).change()
});