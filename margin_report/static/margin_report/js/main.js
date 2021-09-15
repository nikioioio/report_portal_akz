//В данном модуле  происходит возаимодействие с backend отчета
function get_val() {

    //удаляем стэк если он есть
    $(".trace").remove()
    //проверка на незаполненные параметры
    if ($('#month_').val() == '') {
        alert('Введите месяц!!!')
        return
    }
    if ($('#year_').val() == '') {
        alert('Введите год!!!')
        return
    }

    controlFiles = ["АМП и АМД.xlsx",
        "МПФ.xlsx",
        "УКПФ.xlsx",
        "Mapping.xlsx",
        "Коэффициент ценности.xlsx",
        "Остатки на начало года МПФ.xlsx",
        "Остатки на начало года УКПФ.xlsx",
        "Остатки на начало года АМД.xlsx",
        "Остатки на начало года АМП.xlsx",
        "Амортизация.xlsx"]


    var control = document.getElementById("ctrl");
    var data1 = new FormData()

    var arr = control.files
    for (index = 0; index < arr.length; index++) {
        if (arr[index].name == "АМП и АМД.xlsx") {
            data1.append('amp_and_amd', arr[index])
        } else if (arr[index].name == "МПФ.xlsx") {
            data1.append('МПФ', arr[index])
        } else if (arr[index].name == "УКПФ.xlsx") {
            data1.append('УКПФ', arr[index])
        } else if (arr[index].name == "Mapping.xlsx") {
            data1.append('mapping', arr[index])
        } else if (arr[index].name == "Коэффициент ценности.xlsx") {
            data1.append('koef_cen', arr[index])
        } else if (arr[index].name == "Остатки на начало года МПФ.xlsx") {
            data1.append('ost_mpf', arr[index])
        } else if (arr[index].name == "Остатки на начало года УКПФ.xlsx") {
            data1.append('ost_ukpf', arr[index])
        } else if (arr[index].name == "Остатки на начало года АМД.xlsx") {
            data1.append('ost_amd', arr[index])
        } else if (arr[index].name == "Остатки на начало года АМП.xlsx") {
            data1.append('ost_amp', arr[index])
        } else if (arr[index].name == "Амортизация.xlsx") {
            data1.append('amort', arr[index])
        }

    }
    data1.append('year', $('#year_').val());
    data1.append('month', $('#month_').val());

    // const arrControl = Array.from(data1).map(el => el[1].name)
    //
    //
    // const controlFileFunc = () => {
    //     for (let i = 0; i < controlFiles.length; i++) {
    //         if (arrControl.indexOf(controlFiles[i]) === -1) {
    //             alert('Отсутсвует файл ' + controlFiles[i] + ' ,добавьте его')
    //             return false
    //         }
    //
    //     }
    //     return true
    // }
    //
    //
    // if(!controlFileFunc()){
    //     return;
    // }


    // console.log(pr)


    // return
    // data1.append('test', control.files[0])

    var token = '{{ csrf_token }}';
    // alert('csrf generated');

    // $.ajax({
    //     type: 'POST',
    //     url: 'upl/',
    //     data: data1,
    //     processData: false,
    //     contentType: false,
    //     responseType: 'arraybuffer',
    //     headers: {'X-CSRFToken': token},
    //     success: function (data, status, xhr) {
    //
    //         var blob = new Blob([data], {type: 'application/vnd.ms-excel'});
    //         console.log(blob)
    //         var downloadUrl = URL.createObjectURL(blob);
    //         var a = document.createElement("a");
    //         a.href = downloadUrl;
    //         a.download = 'download.xlsx';
    //         document.body.appendChild(a);
    //         a.click();
    //         document.body.removeChild(a);
    //
    //     }
    // })

    let xhr = new XMLHttpRequest();
    xhr.open('POST', 'upl/');
    // xhr.setRequestHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    xhr.responseType = 'arraybuffer';
    $('#circularG').css({'display': 'block'})
    $('#btn_send').attr('disabled', true)
    xhr.onload = function (e) {

        $('#circularG').css({'display': 'none'})
        $('#btn_send').removeAttr('disabled')
        if (this.status == 200) {
            let disposition = this.getResponseHeader('Content-Disposition')

            if (disposition && disposition.indexOf('attachment') !== -1) {
                let filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                let matches = filenameRegex.exec(disposition);
                if (matches != null && matches[1]) filename = matches[1].replace(/['"]/g, '');
            }
            var blob = new Blob([this.response], {type: 'application/vnd.ms-excel'});
            var downloadUrl = URL.createObjectURL(blob);
            var a = document.createElement("a");
            a.href = downloadUrl;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            alert('Отчет сформирован')
        } else {

            function arrayBufferToString(buffer, encoding) {
                return new Promise((resolve, reject) => {

                    var blob = new Blob([buffer], {type: 'text/plain'});
                    var reader = new FileReader();
                    reader.readAsText(blob, encoding);
                    reader.onload = (ev) => {
                        if (ev.target) {
                            resolve(ev.target.result)
                        } else {
                            reject(new Error('Could not convert string to string!'));
                        }
                    }
                })

            }

            arrayBufferToString(this.response, 'UTF-8').then((r) => {
                var decoder = new TextDecoder('utf-8')
                message = JSON.parse(r)['error']
                message1 = JSON.parse(r)['error1']
                // console.log(message)
                $('body').append('<article class="trace">' + message + '</article>').css({'fontsize': '24px'})
                // $('body').append('<article class="trace">'+message1+'</article>').css({'fontsize':'24px'})
                // alert(message)
            })

            // Materialize.toast('Invalid data!', 2000)
        }
    }
    // xhr.onerror = function (ev){
    //     alert('Формирование заверщилось ошибкой')
    // }

    xhr.send(data1);
}