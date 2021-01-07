$(function () {

    function asyncGet(url) {
        // Return a new promise.
        return new Promise(function (resolve, reject) {
            // Do the usual XHR stuff
            var req = new XMLHttpRequest();
            req.open("GET", url, true);

            req.onload = function () {
                // This is called even on 404 etc
                // so check the status
                if (req.status == 200) {
                    // Resolve the promise with the response text
                    resolve(req.response);
                }
                else {
                    // Otherwise reject with the status text
                    // which will hopefully be a meaningful error
                    reject(Error(req.statusText));
                }
            };

            // Handle network errors
            req.onerror = function () {
                reject(Error("Network Error"));
            };

            // Make the request
            req.send();
        });
    }

    function asyncGetJSON(url) {
        return asyncGet(url).then(JSON.parse);
    }

    function asyncPostJSON(url, json_data) {
        // Return a new promise.
        return new Promise(function (resolve, reject) {
            // Do the usual XHR stuff
            var req = new XMLHttpRequest();
            req.open("POST", url, true);

            req.onload = function () {
                // This is called even on 404 etc
                // so check the status
                if (req.status == 200) {
                    // Resolve the promise with the response text
                    resolve(req.response);
                }
                else {
                    // Otherwise reject with the status text
                    // which will hopefully be a meaningful error
                    reject(Error(req.statusText));
                }
            };

            // Handle network errors
            req.onerror = function () {
                reject(Error("Network Error"));
            };

            req.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

            // Make the request
            req.send(JSON.stringify(json_data));
        });
    }

    function convert_utc_to_local(utc_dt) {
        if (!utc_dt) {
            return "";
        }
        utcDateTime = moment.utc(utc_dt);
        localDateTime = utcDateTime.local();
        return localDateTime.format("Y-m-d H:mm:ss");
    }

    function guid() {
        // http://stackoverflow.com/a/105074
        function s4() {
            return Math.floor((1 + Math.random()) * 0x10000).toString(16).substring(1);
        }

        return s4() + s4() + '-' + s4() + '-' + s4() + '-' + s4() + '-' + s4() + s4() + s4();
    }

    function get_survey_data() {
        var data = $("#post-data").val();
        var obj = JSON.parse(data);

        // if no tx_id
        if (!("tx_id" in obj)) {
            // generate uuid
            obj["tx_id"] = guid();
        }

        // if no submitted_at
        if (!("submitted_at" in obj)) {
            // set as current date and time
            obj["submitted_at"] = moment.utc().format("YYYY-MM-DDTHH:mm:ssZ");
        }
        return obj;
    }

    $(".utc_datetime").each(function (index, obj) {
        obj.innerHTML = convert_utc_to_local(obj.innerHTML);
    });

    $("#submit-data").on("click", function (event) {
        event.preventDefault();
        var postData = get_survey_data();
        var quantity = $("#survey-quantity").val();
        $(".alert").hide();
        asyncPostJSON("/submit", {
            "survey": postData,
            "quantity": quantity
        }).then(function (data) {
            $(".alert").removeClass("alert-success alert-danger hidden");
            $(".alert").addClass("alert panel panel--simple panel--success alert-success").text("Posted: " + data);
            $(".alert").show();
        }, function (error) {
            $(".alert").removeClass("alert-success alert-danger hidden");
            $(".alert").addClass("alert panel panel--simple panel--error alert-danger").text("Error during submission");
            $(".alert").show();
            window.alert("Failed submission");
            console.error("Failed!", error);
        });
    });

    $("#validate").on("click", function (event) {
        event.preventDefault();
        var postData = get_survey_data();
        $(".alert").hide();
        asyncPostJSON("/validate", postData).then(function (data) {
            var jsonData = JSON.parse(data);
            if (jsonData.valid === true) {
                $(".alert").removeClass("alert-success alert-danger hidden");
                $(".alert").addClass("alert panel panel--simple panel--success alert-success").text("Validation result: " + data);
                $(".alert").show();
            } else {
                $(".alert").removeClass("alert-success alert-danger hidden");
                $(".alert").addClass("alert panel panel--simple panel--error alert-danger").text("Validation Error. Result: " + data);
                $(".alert").show();
            }
        }, function (error) {
            $(".alert").removeClass("alert-success alert-danger hidden");
            $(".alert").addClass("alert-danger").text("Error during validation submission");
            $(".alert").show();
            window.alert("Failed validation");
            console.error("Failed!", error);
        });
    });

    $("#survey-selector").on("change", function (event) {
        asyncGet("/static/surveys/" + $(event.target).val()).then(function (data) {
            $("#post-data").val(data);
        }, function (error) {
            console.error("Failed!", error);
        });
    });

    var dataTypes = ["pck", "image", "index", "receipt", "json"];
    var currentUrl = window.location.href;
    var dataType = currentUrl.split("/").slice(-1)[0];
    // <host>/FTP will load pck data
    if (dataType === "FTP") { dataType = "pck"; }
    if (dataTypes.includes(dataType)) {
        $("#" + dataType + "-data > tbody > tr").on("click", function (event) {
            var filename = $(event.target).closest("tr").attr("id");
            $("#contentModal .modal-title").text(filename);
            asyncGet("/view/" + dataType + "/" + filename).then(function (data) {
                $("#contentModal .modal-body").html(data);
                $("#contentModal").modal("show");
            }, function (error) {
                console.error("FTP failed!", error);
            });
        });
    }

    // on page load stuff:

    asyncGet("/static/surveys/009.0167.json").then(function (response) {
        $("#post-data").text(response);
    }, function (error) {
        console.error("Failed loading survey 009.0167!", error);
    });

    // Consider putting this javascript into it's own file loaded by the submit page.
    if (currentUrl.endsWith("/submit")) {
        asyncGetJSON("/surveys").then(function (surveys) {
            for (var i = 0; i < surveys.length; i++) {
                $("#survey-selector")
                    .append($("<option>", { value: surveys[i] })
                        .text(surveys[i]));
            }
        }, function (error) {
            console.error("Failed loading surveys!", error);
        });
    }

    $("#refresh-ftp").click(function () {
        location.reload();
    });
});


function checkAll(ele) {
    var checkboxes = document.getElementsByTagName('input');
    if (ele.checked) {
        for (var i = 0; i < checkboxes.length; i++) {
            if (checkboxes[i].type == 'checkbox') {
                checkboxes[i].checked = true;
            }
        }
    } else {
        for (var i = 0; i < checkboxes.length; i++) {
            console.log(i)
            if (checkboxes[i].type == 'checkbox') {
                checkboxes[i].checked = false;
            }
        }
    }
}
