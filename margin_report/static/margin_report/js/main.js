function get_val() {

    // if ($('#month_').val()==''){
    //     alert('Введите месяц!!!')
    //     return
    // }
    // if ($('#year_').val()==''){
    //     alert('Введите год!!!')
    //     return
    // }




    var control = document.getElementById("ctrl");
    var data1 = new FormData()
    var data2 = new FormData()
    // data1.append('dcn', $('#docn').val())
    // data1.append('dc', $('#doc').val())
    // console.log(control.files[1])
    var arr = control.files
    for (index = 0; index < arr.length; index++) {
        if (arr[index].name == "АМП и АМД.xlsx") {
            data1.append('amp_and_amd', arr[index])
        }else if(arr[index].name == "МПФ.xlsx"){
            data1.append('МПФ', arr[index])
        }else if(arr[index].name == "УКПФ.xlsx"){
            data1.append('УКПФ', arr[index])
        }else if(arr[index].name == "Mapping.xlsx"){
            data1.append('mapping', arr[index])
        }else if(arr[index].name == "Коэффициент ценности.xlsx"){
            data1.append('koef_cen', arr[index])
        }else if(arr[index].name == "Остатки на начало года МПФ.xlsx"){
            data1.append('ost_mpf', arr[index])
        }else if(arr[index].name == "Остатки на начало года УКПФ.xlsx"){
            data1.append('ost_ukpf', arr[index])
        }
    }
    data1.append('year', $('#year_').val());
    data1.append('month', $('#month_').val());


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
    $('.cssload-dots').css('display','block')

    xhr.onload = function (e) {

        $('.cssload-dots').css('display','none')
        if (this.status == 200) {
            let disposition = this.getResponseHeader('Content-Disposition')

            if (disposition && disposition.indexOf('attachment') !== -1) {
                let filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                let matches = filenameRegex.exec(disposition);
                if (matches != null && matches[1]) filename = matches[1].replace(/['"]/g, '');
            }
            var blob = new Blob([this.response], { type: 'application/vnd.ms-excel' });
            var downloadUrl = URL.createObjectURL(blob);
            var a = document.createElement("a");
            a.href = downloadUrl;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
        } else {
            Materialize.toast('Invalid data!', 2000);
        }
    }

    xhr.send(data1);
}