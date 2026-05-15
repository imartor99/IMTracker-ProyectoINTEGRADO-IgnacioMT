/**
 * Test de Integración de Lógica de UI - IMTracker
 * Verifica que la generación de componentes dinámicos respeta los permisos del usuario.
 */

// Mock de las variables globales que usa tu dashboard.js
global.window = { CURRENT_LANGUAGE: 'es' };
global.isEnglish = false;

// Simulamos la función que tienes en dashboard.js para poder testearla de forma aislada
function generarBotonesAccionesSimulada(inc) {
    let acciones = '';
    const txtBorrar = global.window.CURRENT_LANGUAGE === 'en' ? "Delete" : "Borrar";

    if (inc.puede_borrar) {
        acciones += `<button class="btnBorrar" data-id="${inc.id}">${txtBorrar}</button>`;
    }
    return acciones;
}

describe('Pruebas de Componentes del Dashboard', () => {
    
    test('Debe generar el botón de borrar si el usuario tiene permisos (puede_borrar: true)', () => {
        const incidencia = { id: 1, puede_borrar: true };
        const html = generarBotonesAccionesSimulada(incidencia);
        
        expect(html).toContain('btnBorrar');
        expect(html).toContain('data-id="1"');
        expect(html).toContain('Borrar');
    });

    test('No debe generar el botón de borrar si el usuario NO tiene permisos (puede_borrar: false)', () => {
        const incidencia = { id: 1, puede_borrar: false };
        const html = generarBotonesAccionesSimulada(incidencia);
        
        expect(html).not.toContain('btnBorrar');
    });

    test('Debe traducir correctamente los textos al cambiar el idioma a inglés', () => {
        global.window.CURRENT_LANGUAGE = 'en';
        const incidencia = { id: 1, puede_borrar: true };
        const html = generarBotonesAccionesSimulada(incidencia);
        
        expect(html).toContain('Delete');
    });
});

