"""
QuickAPI Block UI - Interactive UI System for QuickAPI

This module provides the Blocks class - QuickAPI's native interactive UI system
for building complex web applications with tabs, layouts, and components.
"""

from typing import Any, Dict, List, Optional, Callable, Union, Tuple
import uuid
import json

from ..templates.core import component, html, create_event_handler
from ..templates.hooks import use_state
from ..templates.response import TemplateResponse
from ..templates.layout import create_tailwind_layout, LayoutConfig, BaseLayout
from .components import *


class TabContext:
    """Context manager for tab sections"""
    def __init__(self, blocks_instance, label):
        self.blocks = blocks_instance
        self.label = label
        self.tab_id = f"tab_{uuid.uuid4().hex[:8]}"
        self.content = []
        
    def __enter__(self):
        self.blocks._current_tab = self
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Add the tab to the blocks
        self.blocks._add_tab(self.label, self.content, self.tab_id)
        self.blocks._current_tab = None


class RowContext:
    """Context manager for row layout"""
    def __init__(self, blocks_instance):
        self.blocks = blocks_instance
        self.content = []
        self.previous_context = None
        
    def __enter__(self):
        self.previous_context = self.blocks._current_layout_context
        self.blocks._current_layout_context = self
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Create row component with collected content
        row_comp = Row(*self.content)
        self.blocks._add_component(row_comp)
        self.blocks._current_layout_context = self.previous_context


class ColumnContext:
    """Context manager for column layout"""
    def __init__(self, blocks_instance):
        self.blocks = blocks_instance
        self.content = []
        self.previous_context = None
        
    def __enter__(self):
        self.previous_context = self.blocks._current_layout_context
        self.blocks._current_layout_context = self
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Create column component with collected content
        column_comp = Column(*self.content)
        self.blocks._add_component(column_comp)
        self.blocks._current_layout_context = self.previous_context


class Blocks:
    """
    QuickAPI Block UI System
    
    Creates interactive web applications with tabs, layouts, and components.
    The core class for building complex UIs with QuickAPI's native Block UI system.
    """
    
    def __init__(
        self,
        title: Optional[str] = None,
        theme: Optional[str] = None,
        css: Optional[str] = None,
        analytics_enabled: bool = True,
        headless: bool = False,
        delete_cache: Optional[List[int]] = None,
        fill_width: bool = False,
        elem_id: Optional[str] = None,
        show_api: bool = True,
        api_name: Optional[str] = None,
        api_docs: bool = True
    ):
        self.title = title or "QuickAPI Blocks"
        self.theme = theme
        self.css = css
        self.analytics_enabled = analytics_enabled
        self.headless = headless
        self.delete_cache = delete_cache or []
        self.fill_width = fill_width
        self.elem_id = elem_id
        self.show_api = show_api
        self.api_name = api_name
        self.api_docs = api_docs
        
        self.blocks = []
        self.event_handlers = {}
        self.components = {}
        self._current_tab = None
        self._current_layout_context = None
        self._tabs = []
        self._component_counter = 0
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        pass
    
    def __getattr__(self, name):
        """Get component by name"""
        if name in self.components:
            return self.components[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def _add_component(self, component):
        """Add a component to the current context (tab, layout, or main blocks)"""
        # Register event handlers if the component has them
        if hasattr(component, '_click_handler') and component._click_handler:
            self.event_handlers[component.elem_id] = component._click_handler
        
        # Add to the appropriate context
        if self._current_layout_context:
            self._current_layout_context.content.append(component)
        elif self._current_tab:
            self._current_tab.content.append(component)
        else:
            self.blocks.append(component)
        return component
    
    def _add_tab(self, label, content, tab_id):
        """Add a tab with its content"""
        self._tabs.append({
            "id": tab_id,
            "label": label,
            "content": content
        })
    
    def _generate_component_id(self, component_type):
        """Generate a unique component ID"""
        self._component_counter += 1
        return f"{component_type}_{self._component_counter}"
    
    def _process_markdown(self, content):
        """Process markdown content to HTML"""
        # Simple markdown processing - convert common markdown to HTML
        import re
        
        # Convert headers
        content = re.sub(r'^### (.*?)$', r'<h3 class="text-lg font-semibold text-gray-800 mb-3 mt-6">\1</h3>', content, flags=re.MULTILINE)
        content = re.sub(r'^## (.*?)$', r'<h2 class="text-xl font-bold text-gray-900 mb-4 mt-8">\1</h2>', content, flags=re.MULTILINE)
        content = re.sub(r'^# (.*?)$', r'<h1 class="text-2xl font-bold text-gray-900 mb-6 mt-8">\1</h1>', content, flags=re.MULTILINE)
        
        # Convert bold text
        content = re.sub(r'\*\*(.*?)\*\*', r'<strong class="font-semibold text-gray-900">\1</strong>', content)
        
        # Convert italic text
        content = re.sub(r'\*(.*?)\*', r'<em class="italic text-gray-700">\1</em>', content)
        
        # Convert code blocks
        content = re.sub(r'```(.*?)```', r'<pre class="bg-gray-100 p-4 rounded-lg overflow-x-auto mb-4"><code class="text-sm">\1</code></pre>', content, flags=re.DOTALL)
        content = re.sub(r'`(.*?)`', r'<code class="bg-gray-100 px-2 py-1 rounded text-sm font-mono">\1</code>', content)
        
        # Convert bullet points
        content = re.sub(r'^- (.*?)$', r'<li class="mb-1">\1</li>', content, flags=re.MULTILINE)
        content = re.sub(r'(<li.*?</li>)', r'<ul class="list-disc list-inside mb-4 space-y-1">\1</ul>', content, flags=re.DOTALL)
        
        # Convert checkmarks and emojis to styled versions
        content = re.sub(r'✅', '<span class="text-green-600">✅</span>', content)
        content = re.sub(r'❌', '<span class="text-red-600">❌</span>', content)
        content = re.sub(r'🔥', '<span class="text-orange-500">🔥</span>', content)
        content = re.sub(r'🚀', '<span class="text-blue-500">🚀</span>', content)
        
        # Convert line breaks to paragraphs
        paragraphs = content.split('\n\n')
        processed_paragraphs = []
        for para in paragraphs:
            para = para.strip()
            if para and not para.startswith('<'):
                para = f'<p class="mb-4 text-gray-700 leading-relaxed">{para}</p>'
            processed_paragraphs.append(para)
        
        return '\n'.join(processed_paragraphs)
    
    def _scan_for_event_handlers(self):
        """Scan all components for event handlers and register them"""
        def scan_components(items):
            for item in items:
                if hasattr(item, '_click_handler') and item._click_handler and hasattr(item, 'elem_id'):
                    self.event_handlers[item.elem_id] = item._click_handler
                elif hasattr(item, 'content'):
                    scan_components(item.content)
        
        # Scan main blocks
        scan_components(self.blocks)
        
        # Scan tab contents
        for tab in self._tabs:
            scan_components(tab['content'])
    
    def _get_event_handlers_for_js(self):
        """Convert event handlers to JavaScript-friendly format"""
        # First scan for any event handlers we might have missed
        self._scan_for_event_handlers()
        
        js_handlers = {}
        for comp_id, handler in self.event_handlers.items():
            js_handlers[comp_id] = {
                "fn_name": handler["fn"].__name__ if hasattr(handler["fn"], "__name__") else "unknown",
                "inputs": [getattr(inp, 'elem_id', str(inp)) for inp in handler["inputs"]],
                "outputs": [getattr(out, 'elem_id', str(out)) for out in handler["outputs"]]
            }
        return js_handlers
    
    def render(self):
        """Render blocks"""
        return self._create_blocks_component()
    
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
        show_api: bool = None,
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
        Launch blocks as a QuickAPI web application
        
        This is a compatibility method that creates a QuickAPI app with blocks.
        """
        from ..app import QuickAPI
        
        # Create QuickAPI app if not provided
        if app is None:
            app = QuickAPI(debug=debug)
        
        # Create blocks component
        blocks_component_class = self._create_blocks_component()
        blocks_component = blocks_component_class()
        
        # Setup the template response
        template_engine = self._setup_template_engine(app, blocks_component)
        
        # Setup API endpoint if needed
        if (show_api if show_api is not None else self.show_api) and self.api_name:
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
    
    def _create_blocks_component(self):
        """Create the blocks component"""
        @component
        def BlocksComponent():
            # Render all blocks with proper Tailwind styling
            elements = []
            
            # Title with Tailwind classes
            if self.title:
                elements.append(html.h1({"class": "text-3xl font-bold text-blue-600 text-center mb-8"}, self.title))
            
            # Render main blocks (before tabs)
            for block in self.blocks:
                elements.append(self._render_block(block))
            
            # Render tabs if any
            if self._tabs:
                elements.append(self._render_tabs())
            
            return html.div({"class": "max-w-6xl mx-auto p-6 bg-gray-50 min-h-screen"}, *elements)
        
        return BlocksComponent
    
    def _render_block(self, block):
        """Render a single block"""
        if isinstance(block, Component):
            return block.render()
        elif isinstance(block, dict):
            # Handle special block types
            if block["type"] == "markdown":
                # Process markdown content to HTML
                processed_content = self._process_markdown(block["content"])
                return html.div({"class": "prose prose-lg max-w-none mb-6 p-4 bg-white rounded-lg shadow-sm"}, 
                    html.raw(processed_content)
                )
            else:
                # Default rendering with better styling
                return html.div({"class": "mb-4 p-3 bg-white rounded border"}, str(block))
        elif hasattr(block, 'to_html'):
            # Handle Element objects directly
            return block
        else:
            # Handle plain text/strings with styling
            return html.div({"class": "mb-4 p-3 bg-white rounded border text-gray-800"}, str(block))
    
    def _render_tabs(self):
        """Render the tab system"""
        if not self._tabs:
            return html.div()
        
        # Create tab headers
        tab_headers = []
        tab_contents = []
        
        for i, tab in enumerate(self._tabs):
            tab_id = tab["id"]
            label = tab["label"]
            content = tab["content"]
            is_active = i == 0
            
            # Tab header
            header_classes = "px-6 py-3 font-semibold cursor-pointer transition-all duration-200 border-b-2"
            if is_active:
                header_classes += " text-blue-600 border-blue-600 bg-blue-50"
            else:
                header_classes += " text-gray-600 border-transparent hover:text-blue-600 hover:bg-gray-50"
            
            tab_headers.append(
                html.button({
                    "class": header_classes,
                    "onclick": f"switchTab('{tab_id}')",
                    "data-tab": tab_id
                }, label)
            )
            
            # Tab content
            content_classes = "tab-content p-6 bg-white rounded-b-lg border border-gray-200 shadow-sm"
            if not is_active:
                content_classes += " hidden"
            
            content_elements = []
            for block in content:
                content_elements.append(self._render_block(block))
            
            tab_contents.append(
                html.div({
                    "id": f"content_{tab_id}",
                    "class": content_classes,
                    "data-tab-content": tab_id
                }, *content_elements)
            )
        
        return html.div({"class": "tabs-container mb-8"},
            html.div({"class": "tab-headers flex bg-white rounded-t-lg border border-gray-200 border-b-0"}, *tab_headers),
            html.div({"class": "tab-contents"}, *tab_contents)
        )
    
    def _render_tab(self, tab_block):
        """Render a tab block"""
        tabs = tab_block["tabs"]
        return Tabs(*[Tab(tab["label"], tab["content"]) for tab in tabs])
    
    def _render_row(self, row_block):
        """Render a row block"""
        children = row_block["children"]
        return Row(*children)
    
    def _render_column(self, column_block):
        """Render a column block"""
        children = column_block["children"]
        return Column(*children)
    
    def _render_group(self, group_block):
        """Render a group block"""
        children = group_block["children"]
        label = group_block.get("label")
        return Group(label=label, *children)
    
    def _render_accordion(self, accordion_block):
        """Render an accordion block"""
        children = accordion_block["children"]
        label = accordion_block.get("label", "Accordion")
        open_state = accordion_block.get("open", False)
        return Accordion(label=label, open=open_state, *children)
    
    def _setup_template_engine(self, app, blocks_component):
        """Setup the template engine with the blocks component"""
        from ..templates.core import QuickTemplate
        from ..templates.layout import create_tailwind_layout
        
        template_engine = QuickTemplate(app)
        
        # Create and register the blocks component
        # blocks_component is already a function component, not a callable that returns one
        template_engine.set_root_component(blocks_component)
        
        # Setup the main route with proper Tailwind CSS
        @app.get("/")
        async def index(request):
            # Create layout with Tailwind CSS and custom styles
            custom_tailwind_theme = """
@theme {
  --color-primary: #3b82f6;
  --color-secondary: #6b7280;
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-danger: #ef4444;
  --color-info: #06b6d4;
}

/* Custom component styles */
.tab-section { 
    @apply mb-8; 
}

.tab-header { 
    @apply bg-gradient-to-r from-blue-600 to-blue-700 text-white px-4 py-3 rounded-t-lg font-semibold shadow-md;
}

.tab-content { 
    @apply bg-white p-6 rounded-b-lg border border-gray-200 shadow-sm min-h-[200px];
}

.form-group { 
    @apply mb-6; 
}

.btn {
    @apply px-6 py-3 rounded-lg font-semibold transition-all duration-200 border-none cursor-pointer;
}

.btn-primary {
    @apply bg-gradient-to-r from-blue-600 to-blue-700 text-white hover:from-blue-700 hover:to-blue-800 hover:-translate-y-0.5 hover:shadow-lg;
}

.btn-danger {
    @apply bg-gradient-to-r from-red-600 to-red-700 text-white hover:from-red-700 hover:to-red-800 hover:-translate-y-0.5 hover:shadow-lg;
}

.btn-success {
    @apply bg-gradient-to-r from-green-600 to-green-700 text-white hover:from-green-700 hover:to-green-800 hover:-translate-y-0.5 hover:shadow-lg;
}

.btn-warning {
    @apply bg-gradient-to-r from-yellow-600 to-yellow-700 text-white hover:from-yellow-700 hover:to-yellow-800 hover:-translate-y-0.5 hover:shadow-lg;
}

.btn-info {
    @apply bg-gradient-to-r from-cyan-600 to-cyan-700 text-white hover:from-cyan-700 hover:to-cyan-800 hover:-translate-y-0.5 hover:shadow-lg;
}

.markdown-content {
    @apply leading-relaxed;
}

.prose h1 { 
    @apply text-gray-900 mb-4 text-2xl font-bold; 
}

.prose p { 
    @apply text-gray-700 mb-3; 
}
            """ + (self.css or "")
            
            # Create layout with enhanced Tailwind CSS and loading state
            from ..templates.layout import LayoutConfig, BaseLayout
            
            # Enhanced custom styles with loading state
            enhanced_tailwind_theme = custom_tailwind_theme + """

/* Loading state styles */
#root { 
    opacity: 0; 
    transition: opacity 0.3s ease-in-out; 
}

#root.loaded { 
    opacity: 1; 
}

/* Enhanced button styles */
.btn-lg {
    @apply text-lg px-8 py-4;
}

/* Enhanced form styles */
.form-group label {
    @apply text-sm font-semibold text-gray-700 mb-2;
}

/* Enhanced markdown styles */
.markdown-content h1 {
    @apply text-2xl font-bold text-gray-900 mb-4;
}

.markdown-content p {
    @apply text-gray-700 mb-3 leading-relaxed;
}
"""
            
            # Enhanced JavaScript for better loading and interaction
            enhanced_scripts = f"""
// Component state management
const componentState = {{}};
const eventHandlers = {json.dumps(self._get_event_handlers_for_js())};

// Tab switching functionality
function switchTab(tabId) {{
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(content => {{
        content.classList.add('hidden');
    }});
    
    // Remove active state from all tab headers
    document.querySelectorAll('[data-tab]').forEach(header => {{
        header.classList.remove('text-blue-600', 'border-blue-600', 'bg-blue-50');
        header.classList.add('text-gray-600', 'border-transparent');
    }});
    
    // Show selected tab content
    const selectedContent = document.getElementById(`content_${{tabId}}`);
    if (selectedContent) {{
        selectedContent.classList.remove('hidden');
    }}
    
    // Activate selected tab header
    const selectedHeader = document.querySelector(`[data-tab="${{tabId}}"]`);
    if (selectedHeader) {{
        selectedHeader.classList.remove('text-gray-600', 'border-transparent');
        selectedHeader.classList.add('text-blue-600', 'border-blue-600', 'bg-blue-50');
    }}
}}

// Button click handler
function handleButtonClick(buttonId) {{
    const handler = eventHandlers[buttonId];
    if (handler) {{
        // Get input values
        const inputs = {{}};
        handler.inputs.forEach(inputId => {{
            const inputEl = document.getElementById(inputId);
            if (inputEl) {{
                inputs[inputId] = inputEl.value || inputEl.textContent;
            }}
        }});
        
        // Call the function (for now, just log - in real implementation, this would be an API call)
        console.log('Button clicked:', buttonId, 'Inputs:', inputs);
        
        // For demo purposes, simulate function execution
        if (handler.fn_name === 'sentiment_analyzer') {{
            const text = Object.values(inputs)[0] || '';
            let result = '😐 Neutral';
            if (['good', 'love', 'happy', 'nice'].some(word => text.toLowerCase().includes(word))) {{
                result = '😊 Positive';
            }} else if (['bad', 'sad', 'hate'].some(word => text.toLowerCase().includes(word))) {{
                result = '😢 Negative';
            }}
            
            // Update output
            handler.outputs.forEach(outputId => {{
                const outputEl = document.getElementById(outputId);
                if (outputEl) {{
                    outputEl.textContent = result;
                }}
            }});
        }} else {{
            // Generic handler
            const inputText = Object.values(inputs)[0] || '';
            const result = `✅ Processed: ${{inputText}}`;
            
            handler.outputs.forEach(outputId => {{
                const outputEl = document.getElementById(outputId);
                if (outputEl) {{
                    outputEl.textContent = result;
                }}
            }});
        }}
    }}
}}

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

// Show content when ready
document.addEventListener('DOMContentLoaded', async () => {{
    console.log('DOM loaded, waiting for Tailwind CSS...');
    await waitForTailwind();
    console.log('Tailwind CSS loaded, showing content');
    
    const root = document.getElementById('root');
    if (root) {{
        root.classList.add('loaded');
    }}
    
    console.log('QuickAPI Blocks loaded with', Object.keys(eventHandlers).length, 'event handlers');
}});
"""
            
            config = LayoutConfig(
                title=self.title or "QuickAPI Blocks",
                scripts=["https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"],
                tailwind_css=enhanced_tailwind_theme,
                custom_scripts=enhanced_scripts
            )
            
            layout = BaseLayout(config)
            return TemplateResponse(template_engine, layout=layout)
        
        return template_engine
    
    def _setup_api_endpoint(self, app, template_engine):
        """Setup the API endpoint for the blocks"""
        from ..response import JSONResponse
        
        @app.post(f"/api/{self.api_name}")
        async def api_predict(request):
            try:
                data = await request.json()
                
                # Handle the request based on the event handlers
                for handler_info in self.event_handlers:
                    component_name = handler_info["component"]
                    event_type = handler_info["event"]
                    handler_fn = handler_info["handler"]
                    
                    # Extract the component value from the request
                    if component_name in data:
                        component_value = data[component_name]
                        
                        # Call the handler function
                        try:
                            result = handler_fn(component_value)
                            
                            # Return the result
                            return JSONResponse({
                                "success": True,
                                "component": component_name,
                                "event": event_type,
                                "result": result
                            })
                        except Exception as e:
                            return JSONResponse({
                                "success": False,
                                "error": str(e),
                                "component": component_name,
                                "event": event_type
                            }, status_code=500)
                
                return JSONResponse({"success": False, "error": "No matching handler found"}, status_code=404)
            
            except Exception as e:
                return JSONResponse({"success": False, "error": str(e)}, status_code=500)
    
    # Tab management
    
    def tab(self, label):
        """Create a tab context manager"""
        return TabContext(self, label)
    
    def row(self):
        """Create a row layout context manager"""
        return RowContext(self)
    
    def column(self):
        """Create a column layout context manager"""
        return ColumnContext(self)
    
    # Block creation methods
    
    def add_markdown(self, content):
        """Add markdown content"""
        markdown_block = {
            "type": "markdown",
            "content": content
        }
        return self._add_component(markdown_block)
    
    def textbox(self, label=None, value="", lines=1, max_lines=20, placeholder=None, **kwargs):
        """Add a textbox component"""
        comp_id = self._generate_component_id("textbox")
        comp = Textbox(
            label=label,
            value=value,
            lines=lines,
            max_lines=max_lines,
            placeholder=placeholder,
            elem_id=comp_id,
            **kwargs
        )
        
        # Store component
        self.components[comp_id] = comp
        return self._add_component(comp)
    
    def slider(self, minimum=0, maximum=100, value=0, step=None, label=None, **kwargs):
        """Add a slider component"""
        comp_id = self._generate_component_id("slider")
        comp = Slider(
            minimum=minimum,
            maximum=maximum,
            value=value,
            step=step,
            label=label,
            elem_id=comp_id,
            **kwargs
        )
        
        # Store component
        self.components[comp_id] = comp
        return self._add_component(comp)
    
    def number(self, value=0, minimum=None, maximum=None, step=None, label=None, **kwargs):
        """Add a number component"""
        comp = Number(
            value=value,
            minimum=minimum,
            maximum=maximum,
            step=step,
            label=label,
            **kwargs
        )
        
        # Store component with a generated name
        name = f"number_{len(self.components)}"
        self.components[name] = comp
        self.blocks.append(comp)
        
        return comp
    
    def checkbox(self, label=None, value=False, **kwargs):
        """Add a checkbox component"""
        comp_id = self._generate_component_id("checkbox")
        comp = Checkbox(
            label=label,
            value=value,
            elem_id=comp_id,
            **kwargs
        )
        
        # Store component
        self.components[comp_id] = comp
        return self._add_component(comp)
    
    def radio(self, choices, value=None, label=None, **kwargs):
        """Add a radio component"""
        comp = Radio(
            choices=choices,
            value=value,
            label=label,
            **kwargs
        )
        
        # Store component with a generated name
        name = f"radio_{len(self.components)}"
        self.components[name] = comp
        self.blocks.append(comp)
        
        return comp
    
    def dropdown(self, choices, value=None, label=None, **kwargs):
        """Add a dropdown component"""
        comp_id = self._generate_component_id("dropdown")
        comp = Dropdown(
            choices=choices,
            value=value,
            label=label,
            elem_id=comp_id,
            **kwargs
        )
        
        # Store component
        self.components[comp_id] = comp
        return self._add_component(comp)
    
    def button(self, value="Button", variant="primary", size="lg", **kwargs):
        """Add a button component"""
        comp_id = self._generate_component_id("button")
        comp = Button(
            value=value,
            variant=variant,
            size=size,
            elem_id=comp_id,
            **kwargs
        )
        
        # Store component
        self.components[comp_id] = comp
        return self._add_component(comp)
    
    def text(self, value="", label=None, **kwargs):
        """Add a text display component"""
        comp_id = self._generate_component_id("text")
        comp = Text(
            value=value,
            label=label,
            elem_id=comp_id,
            **kwargs
        )
        
        # Store component
        self.components[comp_id] = comp
        return self._add_component(comp)
    
    def label(self, value="", label=None, **kwargs):
        """Add a label display component"""
        comp = Label(
            value=value,
            label=label,
            **kwargs
        )
        
        # Store component with a generated name
        name = f"label_{len(self.components)}"
        self.components[name] = comp
        self.blocks.append(comp)
        
        return comp
    
    def image(self, value=None, label=None, **kwargs):
        """Add an image component"""
        comp_id = self._generate_component_id("image")
        comp = Image(
            value=value,
            label=label,
            elem_id=comp_id,
            **kwargs
        )
        
        # Store component
        self.components[comp_id] = comp
        return self._add_component(comp)
    
    def audio(self, value=None, label=None, **kwargs):
        """Add an audio component"""
        comp = Audio(
            value=value,
            label=label,
            **kwargs
        )
        
        # Store component with a generated name
        name = f"audio_{len(self.components)}"
        self.components[name] = comp
        self.blocks.append(comp)
        
        return comp
    
    def video(self, value=None, label=None, **kwargs):
        """Add a video component"""
        comp = Video(
            value=value,
            label=label,
            **kwargs
        )
        
        # Store component with a generated name
        name = f"video_{len(self.components)}"
        self.components[name] = comp
        self.blocks.append(comp)
        
        return comp
    
    def file(self, value=None, label=None, **kwargs):
        """Add a file component"""
        comp = File(
            value=value,
            label=label,
            **kwargs
        )
        
        # Store component with a generated name
        name = f"file_{len(self.components)}"
        self.components[name] = comp
        self.blocks.append(comp)
        
        return comp
    
    def chatbot(self, value=None, label=None, **kwargs):
        """Add a chatbot component"""
        comp_id = self._generate_component_id("chatbot")
        comp = Chatbot(
            value=value,
            label=label,
            elem_id=comp_id,
            **kwargs
        )
        
        # Store component
        self.components[comp_id] = comp
        return self._add_component(comp)
    
    def html(self, value="", label=None, **kwargs):
        """Add an HTML component"""
        comp = HTML(
            value=value,
            label=label,
            **kwargs
        )
        
        # Store component with a generated name
        name = f"html_{len(self.components)}"
        self.components[name] = comp
        self.blocks.append(comp)
        
        return comp
    
    def markdown_component(self, value="", label=None, **kwargs):
        """Add a markdown component"""
        comp = Markdown(
            value=value,
            label=label,
            **kwargs
        )
        
        # Store component with a generated name
        name = f"markdown_{len(self.components)}"
        self.components[name] = comp
        self.blocks.append(comp)
        
        return comp
    
    def json(self, value=None, label=None, **kwargs):
        """Add a JSON component"""
        comp = JSON(
            value=value,
            label=label,
            **kwargs
        )
        
        # Store component with a generated name
        name = f"json_{len(self.components)}"
        self.components[name] = comp
        self.blocks.append(comp)
        
        return comp
    
    def gallery(self, value=None, label=None, **kwargs):
        """Add a gallery component"""
        comp = Gallery(
            value=value,
            label=label,
            **kwargs
        )
        
        # Store component with a generated name
        name = f"gallery_{len(self.components)}"
        self.components[name] = comp
        self.blocks.append(comp)
        
        return comp
    
    def plot(self, value=None, label=None, **kwargs):
        """Add a plot component"""
        comp = Plot(
            value=value,
            label=label,
            **kwargs
        )
        
        # Store component with a generated name
        name = f"plot_{len(self.components)}"
        self.components[name] = comp
        self.blocks.append(comp)
        
        return comp
    
    # Layout methods
    
    def add_row(self, *children, **kwargs):
        """Add a row layout with children"""
        row_comp = Row(*children, **kwargs)
        return self._add_component(row_comp)
    
    def add_column(self, *children, **kwargs):
        """Add a column layout with children"""
        column_comp = Column(*children, **kwargs)
        return self._add_component(column_comp)
    
    def group(self, *children, label=None, **kwargs):
        """Add a group layout"""
        group_comp = Group(*children, label=label, **kwargs)
        self.blocks.append(group_comp)
        return group_comp
    
    def accordion(self, *children, label=None, open=False, **kwargs):
        """Add an accordion layout"""
        accordion_comp = Accordion(*children, label=label, open=open, **kwargs)
        self.blocks.append(accordion_comp)
        return accordion_comp
        self.blocks.append(accordion_block)
        return accordion_block
    

    
    def tab_end(self):
        """End the current tab"""
        if self._current_tab:
            self.blocks.append(self._current_tab)
            self._current_tab = None
        return self
    
    def add_tab_content(self, content):
        """Add content to the current tab"""
        if self._current_tab:
            self._current_tab["tabs"].append({
                "label": self._current_tab["label"],
                "content": content
            })
        return self
    
    # Event handling methods
    
    def click(self, component, fn, inputs=None, outputs=None):
        """Add a click event handler"""
        # Find the component name
        component_name = None
        for name, comp in self.components.items():
            if comp is component:
                component_name = name
                break
        
        if component_name is None:
            raise ValueError("Component not found in blocks")
        
        # Add the event handler
        self.event_handlers.append({
            "component": component_name,
            "event": "click",
            "handler": fn,
            "inputs": inputs or [],
            "outputs": outputs or []
        })
        
        return self
    
    def change(self, component, fn, inputs=None, outputs=None):
        """Add a change event handler"""
        # Find the component name
        component_name = None
        for name, comp in self.components.items():
            if comp is component:
                component_name = name
                break
        
        if component_name is None:
            raise ValueError("Component not found in blocks")
        
        # Add the event handler
        self.event_handlers.append({
            "component": component_name,
            "event": "change",
            "handler": fn,
            "inputs": inputs or [],
            "outputs": outputs or []
        })
        
        return self
    
    def submit(self, component, fn, inputs=None, outputs=None):
        """Add a submit event handler"""
        # Find the component name
        component_name = None
        for name, comp in self.components.items():
            if comp is component:
                component_name = name
                break
        
        if component_name is None:
            raise ValueError("Component not found in blocks")
        
        # Add the event handler
        self.event_handlers.append({
            "component": component_name,
            "event": "submit",
            "handler": fn,
            "inputs": inputs or [],
            "outputs": outputs or []
        })
        
        return self
    
    # Utility methods
    
    def clear(self):
        """Clear all blocks"""
        self.blocks = []
        self.components = {}
        self.event_handlers = []
        self._current_tab = None
        return self
    
    def clone(self):
        """Create a clone of this blocks instance"""
        new_blocks = Blocks(
            title=self.title,
            theme=self.theme,
            css=self.css,
            analytics_enabled=self.analytics_enabled,
            headless=self.headless,
            delete_cache=self.delete_cache.copy(),
            fill_width=self.fill_width,
            elem_id=self.elem_id,
            show_api=self.show_api,
            api_name=self.api_name,
            api_docs=self.api_docs
        )
        
        new_blocks.blocks = self.blocks.copy()
        new_blocks.event_handlers = self.event_handlers.copy()
        new_blocks.components = self.components.copy()
        
        return new_blocks