"""
QuickAPI Block UI Interface for QuickAPI

This module provides the Interface class that mimics Block UI's Interface
but integrates with QuickAPI's template system.
"""

from typing import Any, Dict, List, Optional, Callable, Union

from ..templates.core import component, html, create_event_handler
from ..templates.hooks import use_state
from ..templates.response import TemplateResponse
from ..templates.layout import create_tailwind_layout
from .components import *


class Interface:
    """
    Block UI Interface class for QuickAPI
    
    Creates a simple UI around a function with input and output components.
    """
    
    def __init__(
        self,
        fn: Callable,
        inputs: Union[Component, List[Component]] = None,
        outputs: Union[Component, List[Component]] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        article: Optional[str] = None,
        examples: Optional[List[Any]] = None,
        cache_examples: bool = False,
        live: bool = False,
        interpretation: Optional[Union[Callable, str]] = None,
        num_rows: int = 2,
        theme: str = "default",
        css: Optional[str] = None,
        allow_flagging: str = "never",
        flagging_options: List[str] = None,
        analytics_enabled: bool = True,
        batch: bool = False,
        max_batch_size: int = 4,
        api_name: Optional[str] = None,
        api_docs: bool = True,
        headless: bool = False,
        show_error: bool = False,
        show_tips: bool = False,
        enable_queue: bool = False,
        concurrency_limit: Optional[int] = None,
        max_threads: int = 40,
        update: Optional[Callable] = None
    ):
        self.fn = fn
        self.title = title or fn.__name__.replace("_", " ").title()
        self.description = description or f"Interface for {fn.__name__}"
        self.article = article
        self.examples = examples or []
        self.cache_examples = cache_examples
        self.live = live
        self.interpretation = interpretation
        self.num_rows = num_rows
        self.theme = theme
        self.css = css
        self.allow_flagging = allow_flagging
        self.flagging_options = flagging_options or ["incorrect", "offensive", "other"]
        self.analytics_enabled = analytics_enabled
        self.batch = batch
        self.max_batch_size = max_batch_size
        self.api_name = api_name or fn.__name__
        self.api_docs = api_docs
        self.headless = headless
        self.show_error = show_error
        self.show_tips = show_tips
        self.enable_queue = enable_queue
        self.concurrency_limit = concurrency_limit
        self.max_threads = max_threads
        self.update = update
        
        # Normalize inputs and outputs to lists
        self.inputs = inputs if isinstance(inputs, list) else [inputs] if inputs else []
        self.outputs = outputs if isinstance(outputs, list) else [outputs] if outputs else []
        
        # Add default components if none provided
        if not self.inputs:
            self.inputs = [Textbox(label="Input")]
        if not self.outputs:
            self.outputs = [Text(label="Output")]
    
    def launch(
        self,
        app: Optional[Any] = None,
        share: bool = False,
        server_name: Optional[str] = None,
        server_port: Optional[int] = None,
        debug: bool = False,
        auth: Optional[Union[Callable, Tuple[str, str], List[Tuple[str, str]]]] = None,
        auth_message: Optional[str] = None,
        prevent_thread_lock: bool = False,
        show_error: bool = False,
        inbrowser: bool = False,
        favicon_path: Optional[str] = None,
        ssl_verify: bool = True,
        quiet: bool = False,
        show_api: bool = True,
        width: Optional[int] = None,
        height: Optional[int] = None,
        encrypt: bool = False,
        show_tips: bool = False,
        enable_queue: bool = None,
        max_threads: int = 40,
        concurrency_limit: Optional[int] = None,
        **kwargs
    ):
        """
        Launch the interface as a QuickAPI web application
        
        This is a compatibility method that creates a QuickAPI app with the interface.
        """
        from ..app import QuickAPI
        
        # Create the QuickAPI app if not provided
        if app is None:
            app = QuickAPI(debug=debug)
        
        # Create the interface component
        interface_component_class = self._create_interface_component()
        interface_component = interface_component_class()
        
        # Setup the template response
        template_engine = self._setup_template_engine(app, interface_component)
        
        # Setup API endpoint if needed
        if show_api and self.api_name:
            self._setup_api_endpoint(app, template_engine)
        
        # Launch the app
        if not prevent_thread_lock:
            import uvicorn
            host = server_name or "127.0.0.1"
            port = server_port or 7860
            
            if not quiet:
                print(f"Running on {host}:{port}")
            
            uvicorn.run(app, host=host, port=port)
        
        return app
    
    def _create_interface_component(self):
        """Create the interface component"""
        @component
        def InterfaceComponent():
            # State for inputs and outputs
            input_states = []
            for i, input_comp in enumerate(self.inputs):
                if isinstance(input_comp, Textbox):
                    state, set_state = use_state("")
                elif isinstance(input_comp, Slider):
                    state, set_state = use_state(input_comp.value)
                elif isinstance(input_comp, Number):
                    state, set_state = use_state(input_comp.value)
                elif isinstance(input_comp, Checkbox):
                    state, set_state = use_state(input_comp.value)
                elif isinstance(input_comp, Radio):
                    state, set_state = use_state(input_comp.value or (input_comp.choices[0] if input_comp.choices else ""))
                elif isinstance(input_comp, Dropdown):
                    state, set_state = use_state(input_comp.value or (input_comp.choices[0] if input_comp.choices else ""))
                elif isinstance(input_comp, Image):
                    state, set_state = use_state(input_comp.value)
                elif isinstance(input_comp, Audio):
                    state, set_state = use_state(input_comp.value)
                elif isinstance(input_comp, Video):
                    state, set_state = use_state(input_comp.value)
                elif isinstance(input_comp, File):
                    state, set_state = use_state(input_comp.value)
                else:
                    state, set_state = use_state("")
                
                input_states.append((state, set_state))
            
            # State for outputs
            output_states = []
            for i, output_comp in enumerate(self.outputs):
                if isinstance(output_comp, Text):
                    state, set_state = use_state("")
                elif isinstance(output_comp, Label):
                    state, set_state = use_state("")
                elif isinstance(output_comp, Image):
                    state, set_state = use_state("")
                elif isinstance(output_comp, JSON):
                    state, set_state = use_state({})
                else:
                    state, set_state = use_state("")
                
                output_states.append((state, set_state))
            
            # Function to run the model
            def run_model():
                try:
                    # Collect input values
                    input_values = [state for state, _ in input_states]
                    
                    # Call the function
                    result = self.fn(*input_values)
                    
                    # Handle multiple outputs
                    if len(self.outputs) > 1:
                        if not isinstance(result, (list, tuple)):
                            result = [result]
                        for i, (output_state, set_output) in enumerate(output_states):
                            if i < len(result):
                                set_output(result[i])
                    else:
                        # Single output
                        if output_states:
                            _, set_output = output_states[0]
                            set_output(result)
                except Exception as e:
                    if self.show_error:
                        if len(output_states) > 0:
                            _, set_output = output_states[0]
                            set_output(f"Error: {str(e)}")
                    else:
                        print(f"Error running model: {e}")
            
            # Create the UI with enhanced Tailwind classes
            elements = []
            
            # Header section
            header_elements = []
            if self.title:
                header_elements.append(html.h1({"class": "interface-title"}, self.title))
            
            if self.description:
                header_elements.append(html.p({"class": "interface-description"}, self.description))
            
            if header_elements:
                elements.append(html.div({"class": "interface-header"}, *header_elements))
            
            # Input section
            if self.inputs:
                input_elements = []
                for i, input_comp in enumerate(self.inputs):
                    # Set elem_id for proper form handling
                    input_comp.elem_id = f"input_{i}"
                    rendered_input = input_comp.render()
                    input_elements.append(rendered_input)
                
                elements.append(html.div({"class": "interface-card"},
                    html.h3({"class": "section-title"}, "📝 Input"),
                    *input_elements
                ))
            
            # Submit button with enhanced styling
            elements.append(html.button({
                "class": "submit-button",
                "onclick": "runModel()"
            }, "🚀 Run Model"))
            
            # Output section
            if self.outputs:
                output_elements = []
                for i, output_comp in enumerate(self.outputs):
                    # Set the elem_id for the output component
                    output_comp.elem_id = f"output_{i}"
                    
                    # Create a styled output container
                    if isinstance(output_comp, (Text, Label)):
                        output_elements.append(
                            html.div({"class": "form-group"},
                                html.label({"class": "block text-sm font-semibold text-gray-700 mb-2"}, 
                                    output_comp.label or f"Output {i+1}"),
                                html.div({
                                    "id": f"output_{i}",
                                    "class": "output-container"
                                }, output_comp.value or "Output will appear here...")
                            )
                        )
                    else:
                        rendered_output = output_comp.render()
                        output_elements.append(rendered_output)
                
                elements.append(html.div({"class": "interface-card"},
                    html.h3({"class": "section-title"}, "📊 Output"),
                    *output_elements
                ))
            
            # Article section
            if self.article:
                elements.append(html.div({"class": "interface-card mt-8"},
                    html.h3({"class": "section-title"}, "📖 Additional Information"),
                    html.div({"class": "prose prose-lg max-w-none text-gray-700"}, self.article)
                ))
            
            return html.div({"class": "max-w-5xl mx-auto p-8 bg-gradient-to-br from-gray-50 to-gray-100 min-h-screen"}, 
                *elements
            )
        
        return InterfaceComponent
    
    def _setup_template_engine(self, app, interface_component):
        """Setup the template engine with the interface component"""
        from ..templates.core import QuickTemplate
        from ..templates.layout import LayoutConfig, BaseLayout
        
        template_engine = QuickTemplate(app)
        
        # Create and register the interface component
        template_engine.set_root_component(interface_component)
        
        # Setup the main route with enhanced Tailwind CSS
        @app.get("/")
        async def index(request):
            # Enhanced Tailwind theme for Interface
            enhanced_tailwind_theme = """
@theme {
  --color-primary: #3b82f6;
  --color-secondary: #6b7280;
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-danger: #ef4444;
  --color-info: #06b6d4;
}

/* Enhanced Interface styles */
#root { 
    opacity: 0; 
    transition: opacity 0.3s ease-in-out; 
}

#root.loaded { 
    opacity: 1; 
}

/* Form component styles */
.form-group { 
    @apply mb-6; 
}

.form-group label {
    @apply block text-sm font-semibold text-gray-700 mb-2;
}

/* Input styles */
input[type="text"], input[type="number"], input[type="range"], textarea, select {
    @apply w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200;
}

input[type="range"] {
    @apply h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer;
}

input[type="range"]::-webkit-slider-thumb {
    @apply appearance-none w-5 h-5 bg-blue-600 rounded-full cursor-pointer shadow-md;
}

/* Button styles */
.submit-button {
    @apply w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white font-semibold py-4 px-6 rounded-lg hover:from-blue-700 hover:to-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-200 transform hover:-translate-y-0.5 hover:shadow-lg;
}

/* Output styles */
.output-container {
    @apply p-4 bg-gray-50 rounded-lg border border-gray-200 min-h-[80px] text-gray-800 font-mono text-sm;
}

/* Card styles */
.interface-card {
    @apply bg-white rounded-xl shadow-lg border border-gray-100 p-6 mb-6;
}

.interface-header {
    @apply text-center mb-8;
}

.interface-title {
    @apply text-4xl font-bold text-gray-900 mb-4;
}

.interface-description {
    @apply text-lg text-gray-600 leading-relaxed;
}

.section-title {
    @apply text-xl font-semibold text-gray-800 mb-4 flex items-center;
}

.section-title::before {
    @apply content-[''] w-1 h-6 bg-blue-600 rounded-full mr-3;
}
            """ + (self.css or "")
            
            # Enhanced JavaScript for better loading and interaction
            enhanced_scripts = f"""
// Enhanced Tailwind loading detection
function waitForTailwind() {{
    return new Promise((resolve) => {{
        let attempts = 0;
        const maxAttempts = 60; // 3 seconds max
        
        function checkTailwind() {{
            attempts++;
            
            // Create test element with Tailwind classes
            const testEl = document.createElement('div');
            testEl.className = 'bg-blue-500 p-4 rounded-lg';
            testEl.style.position = 'absolute';
            testEl.style.left = '-9999px';
            testEl.style.top = '-9999px';
            document.body.appendChild(testEl);
            
            const computedStyle = window.getComputedStyle(testEl);
            const bgColor = computedStyle.backgroundColor;
            const padding = computedStyle.padding;
            const borderRadius = computedStyle.borderRadius;
            
            document.body.removeChild(testEl);
            
            // Check if Tailwind styles are applied
            const isTailwindLoaded = (
                bgColor && bgColor.includes('59, 130, 246') && // blue-500
                padding && padding !== '0px' &&
                borderRadius && borderRadius !== '0px'
            );
            
            if (isTailwindLoaded || attempts >= maxAttempts) {{
                resolve();
            }} else {{
                setTimeout(checkTailwind, 50);
            }}
        }}
        
        // Start checking immediately
        checkTailwind();
    }});
}}

// Enhanced model runner
async function runModel() {{
    try {{
        // Show loading state
        const submitBtn = document.querySelector('.submit-button');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = '⏳ Processing...';
        submitBtn.disabled = true;
        
        // Collect input values from the actual form elements
        const inputs = document.querySelectorAll('input, textarea, select');
        const inputData = {{}};
        
        inputs.forEach((input, index) => {{
            if (input.type === 'range' || input.type === 'number') {{
                inputData[`input_${{index}}`] = parseFloat(input.value) || 0;
            }} else if (input.type === 'checkbox') {{
                inputData[`input_${{index}}`] = input.checked;
            }} else {{
                inputData[`input_${{index}}`] = input.value || '';
            }}
        }});
        
        console.log('🚀 Sending data:', inputData);
        
        const response = await fetch('/api/{self.api_name}', {{
            method: 'POST',
            headers: {{
                'Content-Type': 'application/json',
            }},
            body: JSON.stringify(inputData)
        }});
        
        const result = await response.json();
        console.log('✅ Received result:', result);
        
        if (result.success) {{
            // Update output elements with animation
            const outputs = document.querySelectorAll('[id^="output_"]');
            outputs.forEach((output, index) => {{
                const outputKey = `output_${{index}}`;
                if (result.data[outputKey] !== undefined) {{
                    // Add fade effect
                    output.style.opacity = '0.5';
                    setTimeout(() => {{
                        output.textContent = result.data[outputKey];
                        output.style.opacity = '1';
                    }}, 150);
                }}
            }});
        }} else {{
            console.error('❌ Error:', result.error);
            // Show error in first output
            const firstOutput = document.querySelector('[id^="output_"]');
            if (firstOutput) {{
                firstOutput.textContent = '❌ Error: ' + (result.error || 'Unknown error');
                firstOutput.style.color = '#ef4444';
            }}
        }}
    }} catch (error) {{
        console.error('❌ Network Error:', error);
        // Show error in first output
        const firstOutput = document.querySelector('[id^="output_"]');
        if (firstOutput) {{
            firstOutput.textContent = '❌ Network Error: ' + error.message;
            firstOutput.style.color = '#ef4444';
        }}
    }} finally {{
        // Reset button state
        const submitBtn = document.querySelector('.submit-button');
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }}
}}

// Show content when ready
document.addEventListener('DOMContentLoaded', async () => {{
    console.log('🎨 DOM loaded, waiting for Tailwind CSS...');
    await waitForTailwind();
    console.log('✅ Tailwind CSS loaded, showing content');
    
    const root = document.getElementById('root');
    if (root) {{
        root.classList.add('loaded');
    }}
    
    console.log('🚀 QuickAPI Interface ready!');
}});
"""
            
            config = LayoutConfig(
                title=self.title or "QuickAPI Interface",
                scripts=["https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"],
                tailwind_css=enhanced_tailwind_theme,
                custom_scripts=enhanced_scripts
            )
            
            layout = BaseLayout(config)
            return TemplateResponse(template_engine, layout=layout)
        
        return template_engine
    
    def _setup_api_endpoint(self, app, template_engine):
        """Setup the API endpoint for the interface"""
        from ..response import JSONResponse
        
        @app.post(f"/api/{self.api_name}")
        async def api_predict(request):
            try:
                data = await request.json()
                
                # Extract input values from the request
                input_values = []
                for i, input_comp in enumerate(self.inputs):
                    if isinstance(input_comp, Textbox):
                        input_values.append(data.get(f"input_{i}", ""))
                    elif isinstance(input_comp, Slider):
                        input_values.append(data.get(f"input_{i}", 0))
                    elif isinstance(input_comp, Number):
                        input_values.append(data.get(f"input_{i}", 0))
                    elif isinstance(input_comp, Checkbox):
                        input_values.append(data.get(f"input_{i}", False))
                    elif isinstance(input_comp, Radio):
                        input_values.append(data.get(f"input_{i}", ""))
                    elif isinstance(input_comp, Dropdown):
                        input_values.append(data.get(f"input_{i}", ""))
                    else:
                        input_values.append(data.get(f"input_{i}", ""))
                
                # Call the function
                result = self.fn(*input_values)
                
                # Handle multiple outputs
                if len(self.outputs) > 1:
                    if not isinstance(result, (list, tuple)):
                        result = [result]
                    output_dict = {}
                    for i, output in enumerate(result):
                        output_dict[f"output_{i}"] = output
                    response_data = {"success": True, "data": output_dict}
                else:
                    response_data = {"success": True, "data": {"output_0": result}}
                
                return JSONResponse(response_data)
            
            except Exception as e:
                error_response = {"success": False, "error": str(e)}
                return JSONResponse(error_response, status_code=500)
    
    def predict(self, *args, **kwargs):
        """Make a prediction using the interface function"""
        return self.fn(*args, **kwargs)
    
    def test_inputs(self, *test_inputs):
        """Test the interface with sample inputs"""
        return self.fn(*test_inputs)
    
    def save(self, filepath: str):
        """Save the interface configuration to a file"""
        import json
        
        config = {
            "title": self.title,
            "description": self.description,
            "article": self.article,
            "examples": self.examples,
            "live": self.live,
            "theme": self.theme,
            "css": self.css,
            "allow_flagging": self.allow_flagging,
            "flagging_options": self.flagging_options,
            "api_name": self.api_name,
            "api_docs": self.api_docs,
            "inputs": [],
            "outputs": []
        }
        
        # Save input configurations
        for input_comp in self.inputs:
            input_config = {
                "type": input_comp.__class__.__name__,
                "label": input_comp.label,
                "value": input_comp.value
            }
            
            # Add type-specific properties
            if isinstance(input_comp, Slider):
                input_config.update({
                    "minimum": input_comp.minimum,
                    "maximum": input_comp.maximum,
                    "step": input_comp.step
                })
            elif isinstance(input_comp, Radio):
                input_config["choices"] = input_comp.choices
            elif isinstance(input_comp, Dropdown):
                input_config["choices"] = input_comp.choices
            
            config["inputs"].append(input_config)
        
        # Save output configurations
        for output_comp in self.outputs:
            output_config = {
                "type": output_comp.__class__.__name__,
                "label": output_comp.label,
                "value": output_comp.value
            }
            config["outputs"].append(output_config)
        
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)
    
    @classmethod
    def load(cls, filepath: str):
        """Load an interface from a configuration file"""
        import json
        
        with open(filepath, 'r') as f:
            config = json.load(f)
        
        # Recreate input components
        inputs = []
        for input_config in config.get("inputs", []):
            comp_type = input_config["type"]
            
            if comp_type == "Textbox":
                comp = Textbox(
                    label=input_config["label"],
                    value=input_config["value"]
                )
            elif comp_type == "Slider":
                comp = Slider(
                    label=input_config["label"],
                    value=input_config["value"],
                    minimum=input_config.get("minimum", 0),
                    maximum=input_config.get("maximum", 100),
                    step=input_config.get("step", 1)
                )
            elif comp_type == "Number":
                comp = Number(
                    label=input_config["label"],
                    value=input_config["value"]
                )
            elif comp_type == "Checkbox":
                comp = Checkbox(
                    label=input_config["label"],
                    value=input_config["value"]
                )
            elif comp_type == "Radio":
                comp = Radio(
                    label=input_config["label"],
                    value=input_config["value"],
                    choices=input_config.get("choices", [])
                )
            elif comp_type == "Dropdown":
                comp = Dropdown(
                    label=input_config["label"],
                    value=input_config["value"],
                    choices=input_config.get("choices", [])
                )
            elif comp_type == "Image":
                comp = Image(
                    label=input_config["label"],
                    value=input_config["value"]
                )
            else:
                comp = Textbox(
                    label=input_config["label"],
                    value=input_config["value"]
                )
            
            inputs.append(comp)
        
        # Recreate output components
        outputs = []
        for output_config in config.get("outputs", []):
            comp_type = output_config["type"]
            
            if comp_type == "Text":
                comp = Text(
                    label=output_config["label"],
                    value=output_config["value"]
                )
            elif comp_type == "Label":
                comp = Label(
                    label=output_config["label"],
                    value=output_config["value"]
                )
            elif comp_type == "Image":
                comp = Image(
                    label=output_config["label"],
                    value=output_config["value"],
                    interactive=False
                )
            elif comp_type == "JSON":
                comp = JSON(
                    label=output_config["label"],
                    value=output_config["value"]
                )
            else:
                comp = Text(
                    label=output_config["label"],
                    value=output_config["value"]
                )
            
            outputs.append(comp)
        
        # Create a dummy function for the interface
        def dummy_fn(*args):
            return "This interface was loaded from a configuration file."
        
        # Create the interface
        interface = cls(
            fn=dummy_fn,
            inputs=inputs,
            outputs=outputs,
            title=config.get("title"),
            description=config.get("description"),
            article=config.get("article"),
            examples=config.get("examples", []),
            live=config.get("live", False),
            theme=config.get("theme", "default"),
            css=config.get("css"),
            allow_flagging=config.get("allow_flagging", "never"),
            flagging_options=config.get("flagging_options", ["incorrect", "offensive", "other"]),
            api_name=config.get("api_name", "predict"),
            api_docs=config.get("api_docs", True)
        )
        
        return interface