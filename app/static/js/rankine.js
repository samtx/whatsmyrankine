function formatData(val, prop) {
    
}

$SCRIPT_ROOT = {{ request.script_root | tojson | safe }};
$(function() {
    
    function getUnits() {
        // Get unit conversion factors
        console.log($('#units').val()); 
            if ($('#units').val() == 'SI') {
                console.log('yes!');
                var units = {
                    useSI: true,
                    pressureFactor: 0.00689476,  //  lbf/in2 to MPa 
                    energyFactor: 2.326, //     Btu/lbm to kJ/kg 
                    tempFactor: 5.0/9.0, //     def F to deg C
                    tempShift: -32,  //  tempFactor * T + tempShift
                    entropyFactor: 4.1868,  // Btu/lb R to kJ/kg K 
                    volumeFactor: 0.062428,  //   ft3/lb to m3/kg
                    
                    pressureUnits: 'MPa',
                    tempUnits: '&deg;C',
                    energyUnits: 'kJ/kg',
                    entropyUnits: 'kJ/kg K',
                    volumeUnits: 'm<sup>3</sup>/kg'
                };
                
            }
            else {
                var units = {
                    useSI: false,
                    pressureFactor: 1/0.00689476,  //  MPa to lbf/in2
                    energyFactor: 1/2.326, //    kJ/kg to Btu/lbm
                    tempFactor: 9.0/5.0, //     deg C to deg F
                    tempShift: +32,  //  tempFactor * T + tempShift
                    entropyFactor: 1/4.1868,  // kJ/kg K to Btu/lb R
                    volumeFactor:1/0.062428,  //  m3/kg to ft3/lb
                    
                    pressureUnits: 'lbf/in<sup>2</sup>',
                    tempUnits: '&deg;F',
                    energyUnits: 'Btu/lb',
                    entropyUnits: 'Btu/lb &deg;R',
                    volumeUnits: 'ft<sup>3</sup>/lb'
                }
            };
            return units;
    };
    
    $('#units').on('change', function() {
        // Use correct units in form input
        units = getUnits()
        // $('#cycle-params').find('.tempUnits').html(tempUnits);
        oldLowPressure = $('#lowPressure').val();
        oldHighPressure = $('#highPressure').val();
        $('#lowPressure').val(oldLowPressure*=units.pressureFactor);
        $('#highPressure').val(oldHighPressure*=units.pressureFactor);
        $('#cycle-params').find('.pressureUnits').html(units.pressureUnits);
    });
    
    $('#runcycle').on('click', function() {
        if ($('#units').val() == 'SI') {
                var useSI = true;
            }
            else {
                var useSI = false;
            }
        $.getJSON($SCRIPT_ROOT + '/_runcycle', {
            workingFluid: $('#workingFluid').val(),
            highPressure: $('#highPressure').val(),
            lowPressure: $('#lowPressure').val(),
            // maxTemperature: $('#maxTemperature').val(),
            turbineEfficiency: $('#turbineEfficiency').val()/100.0,
            pumpEfficiency: $('#pumpEfficiency').val()/100.0,
            useSI: useSI
            
            
            // massFlowRate: $('#massFlowRate').val(),
            // units: $('#units').val()
        }, function(data) {
            console.table(data);
            $("#thermEff").text(parseFloat(data.cycle.en_eff*100).toFixed(2) + ' %');
            $("#bwr").text(parseFloat(data.cycle.bwr).toExponential(2));
            $("#exEff").text(parseFloat(data.cycle.ex_eff*100).toFixed(2) + ' %');
            
            // update state table with data
            // var $table = $('#stateTableBody');
            // $table.empty();
            
            // Get correct unit conversions and headers
            units = getUnits();
                                
            // Populate State Table
            var rows = '';
            states = data.cycle.states;
            for (var i=0, l=states.length; i<l; i++) {
                state = states[i];
                var row = '<tr>';
                console.log(state);
                row += '<td>' + state['name'] + '</td>';
                row += '<td>'+(units.tempFactor*parseFloat(state['T'])+units.tempShift).toFixed(1)+'</td>';
                row += '<td>'+(units.pressureFactor*parseFloat(state['p'])).toFixed(2)+'</td>';
                row += '<td>'+(units.volumeFactor*parseFloat(state['v'])).toExponential(4)+'</td>';
                row += '<td>'+(units.energyFactor*parseFloat(state['h'])).toFixed(2)+'</td>';
                row += '<td>'+(units.entropyFactor*parseFloat(state['s'])).toFixed(4)+'</td>';
                row += '<td>'+(units.energyFactor*parseFloat(state['ef'])).toFixed(2)+'</td>';
                x = state['x'];
                row += '<td>';
                if (isNaN(parseFloat(x))) {
                    row += x;
                } else {
                    row += parseFloat(x).toFixed(2);
                }
                row += '</td>';
                console.log(row);
                rows += row + '</tr>';
            }
            console.log(rows);
            $('#stateTable > tbody').html(rows);
            
            // Populate Process Table
            var rows = '';
            var heatTotal = 0.0;
            var workTotal = 0.0;
            processes = data.cycle.processes;
            for (var i=0, l=processes.length; i<l; i++) {
                process = processes[i];
                var row = '<tr>';
                console.log(process);
                row += '<td>' + process['name'] + '</td>';
                row += '<td>' + process['state_in'] + ' &#10145; ' + process['state_out'] + '</td>';
                heat = parseFloat(process['heat'])*units.energyFactor;
                work = parseFloat(process['work'])*units.energyFactor;
                row += '<td style="text-align:right">' +  heat.toFixed(2) + '</td><td style="text-align:right">' + work.toFixed(2) + '</td></tr>';
                rows += row
                heatTotal += heat;
                workTotal += work;
                console.log(row);
            }
            $('#processTable > tbody').html(rows);
            $('#heatTotal').text(heatTotal.toFixed(2));
            $('#workTotal').text(workTotal.toFixed(2));
            
            // Use correct units in table headers
            $('table').find('.tempUnits').html(units.tempUnits);
            $('table').find('.pressureUnits').html(units.pressureUnits);
            $('table').find('.volumeUnits').html(units.volumeUnits);
            $('table').find('.energyUnits').html(units.energyUnits);
            $('table').find('.entropyUnits').html(units.entropyUnits);
            $('#stateTable').find('tr').css('text-align', 'right');
        });
        return false;
    });
});
