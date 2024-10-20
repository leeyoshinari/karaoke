const server = localStorage.getItem("server");
document.getElementById("file-upload").addEventListener('click', () => {
    let fileUpload_input = document.getElementById("file-input");
    fileUpload_input.click();
    fileUpload_input.onchange = function (event) {
        show_modal_cover();
        let files = event.target.files;
        let total_files = files.length;
        if (total_files < 1) {
            close_modal_cover();
            return;
        }
        let success_num = 0;
        let fast_upload_num = 0;
        let failure_num = 0;
        let failure_file = [];

        for (let i=0; i<total_files; i++) {
            let form_data = new FormData();
            form_data.append("file", files[i]);
            form_data.append("index", (i + 1).toString());
            form_data.append("total", total_files.toString());

            let xhr = new XMLHttpRequest();
            xhr.open("POST", server + "/song/upload");
            xhr.setRequestHeader("processData", "false");
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4) {
                    if(xhr.status === 200) {
                        let res = JSON.parse(xhr.responseText);
                        if (res['code'] === 0) {
                            success_num += 1;
                        } else {
                            failure_num += 1;
                            failure_file.push(res['data']);
                        }
                    }
                    if ((success_num + fast_upload_num + failure_num) === total_files) {
                        let msg = "";
                        let level = "success";
                        if (success_num > 0) {
                            msg += success_num + "个文件上传成功";
                        }
                        if (failure_num > 0) {
                            if (msg.length > 0) {msg += '，';}
                            msg += failure_num + "个文件上传失败";
                            level = "error";
                        }
                        $.Toast(msg, level);
                        if (failure_num > 0) {
                            let s = "";
                            for (let i=0; i<failure_file.length; i++) {
                                s += failure_file[i] + "，";
                            }
                            $.Toast(s, 'error');
                        }
                    }
                }
                fileUpload_input.value = '';
                close_modal_cover();
                get_song_list();
            }
            xhr.send(form_data);
        }
    }
})

document.getElementById("search").addEventListener('click', () => {get_song_list();})

document.getElementById("generate_code").addEventListener('click', () => {
    let qrcodeEle = document.getElementsByClassName("qrcode")[0];
    if (qrcodeEle.style.display !== "block") {
        let qrcode = new QRCode(document.getElementById("qrcode"), {
            text: window.location.protocol + "//" + window.location.host + server + "/song",
            width: 200,
            height: 200,
            colorDark: "#000000",
            colorLight: "#ffffff",
            correctLevel: QRCode.CorrectLevel.H
        });
        qrcodeEle.style.display = "block";
    } else {
        qrcodeEle.style.display = "none";
        document.getElementById("qrcode").innerHTML = '';
    }
})

function get_song_list(page=1) {
    let q = document.getElementById("file-search").value;
    let params = "page=" + page;
    if (q && q !== "" && q !== null) {
        params = params + "&q=" + q;
    }
    $.ajax({
        type: "GET",
        url: server + "/song/list?" + params,
        success: function (data) {
            let s = '';
            if (data.code === 0) {
                if (data.total === 0) {
                    $.Toast("没有歌曲", "error");
                    return;
                }
                data.data.forEach(item => {
                    s = s + `<tr><td>${item.name}</td><td>${item.create_time}</td>
                            <td><a onclick="sing_song(${item.id})">点歌</a><a onclick="delete_song(${item.id})">删除</a></td></tr>`;
                })
                PagingManage($('#paging'), data.totalPage, data.page);
                document.getElementsByTagName("table")[0].style.display = "";
                document.getElementById("create-time").style.display = "";
                document.getElementsByTagName("tbody")[0].innerHTML = s;
            } else {
                $.Toast(data.msg, 'error');
            }
        }
    })
}

function get_history_list(queryType) {
    $.ajax({
        type: "GET",
        url: server + "/song/singHistory/" + queryType,
        success: function (data) {
            let s = '';
            if (data.code === 0) {
                if (data.total === 0) {
                    $.Toast("没有歌曲", "error");
                    return;
                }
                data.data.forEach(item => {
                    s = s + `<tr><td>${item.name}</td><td><a onclick="sing_song(${item.id})">点歌</a><a onclick="delete_from_list(${item.id})">删除</a></td></tr>`;
                })
                PagingManage($('#paging'), data.totalPage, data.page);
                document.getElementsByTagName("table")[0].style.display = "";
                document.getElementById("create-time").style.display = "none";
                document.getElementsByTagName("tbody")[0].innerHTML = s;
            } else {
                $.Toast(data.msg, 'error');
            }
        }
    })
}

function delete_song(file_id) {
    $.ajax({
        type: "GET",
        url: server + "/song/delete/" + file_id,
        success: function (data) {
            if (data.code === 0) {
                $.Toast(data.msg, "success");
                get_song_list();
                get_added_songs();
            } else {
                $.Toast(data.msg, "error");
            }
        }
    })
}

function sing_song(file_id) {
    $.ajax({
        type: "GET",
        url: server + "/song/sing/" + file_id,
        success: function (data) {
            if (data.code === 0) {
                get_added_songs();
                $.Toast(data.msg, "success");
            } else {
                $.Toast(data.msg, "error");
            }
        }
    })
}

function get_added_songs() {
    $.ajax({
        type: "GET",
        url: server + "/song/singHistory/pendingAll",
        success: function (data) {
            if (data.code === 0) {
                document.getElementById("addSongs").innerText = data.total;
            } else {
                $.Toast(data.msg, "error");
            }
        }
    })
}

function delete_from_list(file_id) {
    $.ajax({
        type: "GET",
        url: server + "/song/deleteHistory/" + file_id,
        success: function (data) {
            if (data.code !== 0) {
                console.log(data.msg);
            }
        }
    })
}

function show_modal_cover() {
    $('.modal_cover')[0].style.display = 'flex';
    $('.modal_cover>.modal_gif')[0].style.display = 'flex';
}

function close_modal_cover() {
    $('.modal_cover')[0].style.display = 'none';
    $('.modal_cover>.modal_gif')[0].style.display = 'none';
}

window.onload = function() {
    get_song_list();
    setTimeout(() => {get_added_songs();}, 500);
};
