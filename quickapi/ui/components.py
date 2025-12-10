"""
QuickAPI UI Components - Block UI-like components for QuickAPI

This module provides a comprehensive set of UI components that mimic Block UI's
interface but integrate with QuickAPI's template system.
"""

from typing import Any, Dict, List, Optional, Callable, Union, Tuple
from dataclasses import dataclass, field

from ..templates.core import Element, html


@dataclass
class Component:
    """Base class for all UI components"""
    label: Optional[str] = None
    value: Any = None
    interactive: bool = True
    visible: bool = True
    elem_id: Optional[str] = None
    elem_classes: List[str] = field(default_factory=list)
    every: Optional[float] = None
    show_label: bool = True
    scale: int = 1
    min_width: int = 160
    
    def get_props(self) -> Dict[str, Any]:
        """Get component properties as a dictionary"""
        props = {}
        
        if self.elem_id:
            props["id"] = self.elem_id
            
        if self.elem_classes:
            props["class_"] = " ".join(self.elem_classes)
            
        if not self.visible:
            props["style"] = "display: none;"
            
        return props
    
    def render(self) -> Element:
        """Render the component as an Element"""
        raise NotImplementedError("Subclasses must implement render method")


class Textbox(Component):
    """Text input component"""
    
    def __init__(
        self,
        label: Optional[str] = None,
        value: str = "",
        lines: int = 1,
        max_lines: int = 20,
        placeholder: Optional[str] = None,
        show_label: bool = True,
        interactive: bool = True,
        elem_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            label=label,
            value=value,
            interactive=interactive,
            elem_id=elem_id,
            show_label=show_label,
            **kwargs
        )
        self.lines = lines
        self.max_lines = max_lines
        self.placeholder = placeholder
    
    def render(self) -> Element:
        """Render the textbox component"""
        props = self.get_props()
        
        # Add Tailwind classes
        base_classes = "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        if props.get("class_"):
            props["class_"] = f"{base_classes} {props['class_']}"
        else:
            props["class_"] = base_classes
        
        if self.lines == 1:
            # Single line text input
            input_props = {
                "type": "text",
                "value": self.value,
                "placeholder": self.placeholder or "",
                **({"disabled": ""} if not self.interactive else {})
            }
            input_elem = html.input({**props, **input_props})
        else:
            # Multi-line textarea
            textarea_props = {
                "rows": str(self.lines),
                "placeholder": self.placeholder or "",
                **({"disabled": ""} if not self.interactive else {})
            }
            input_elem = html.textarea({**props, **textarea_props}, self.value)
        
        # Add label if needed
        if self.show_label and self.label:
            return html.div({"class": "form-group mb-4"},
                html.label({"for": self.elem_id or "textbox", "class": "block text-sm font-medium text-gray-700 mb-2"}, self.label),
                input_elem
            )
        
        return input_elem


class Slider(Component):
    """Slider component for numeric values"""
    
    def __init__(
        self,
        minimum: float = 0,
        maximum: float = 100,
        value: Union[float, Tuple[float, float]] = 0,
        step: Optional[float] = None,
        label: Optional[str] = None,
        show_label: bool = True,
        interactive: bool = True,
        elem_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            label=label,
            value=value,
            interactive=interactive,
            elem_id=elem_id,
            show_label=show_label,
            **kwargs
        )
        self.minimum = minimum
        self.maximum = maximum
        self.step = step or 1
    
    def render(self) -> Element:
        """Render the slider component"""
        props = self.get_props()
        
        # Add Tailwind classes for slider
        base_classes = "w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
        if props.get("class_"):
            props["class_"] = f"{base_classes} {props['class_']}"
        else:
            props["class_"] = base_classes
        
        input_props = {
            "type": "range",
            "min": str(self.minimum),
            "max": str(self.maximum),
            "step": str(self.step),
            "value": str(self.value),
            **({"disabled": ""} if not self.interactive else {})
        }
        
        slider_elem = html.input({**props, **input_props})
        
        # Add value display with Tailwind classes
        value_display = html.span({"class": "text-sm font-medium text-gray-700 min-w-[40px] text-center"}, str(self.value))
        
        # Add label if needed
        if self.show_label and self.label:
            return html.div({"class": "form-group mb-4"},
                html.label({"for": self.elem_id or "slider", "class": "block text-sm font-medium text-gray-700 mb-2"}, self.label),
                html.div({"class": "flex items-center space-x-3"},
                    slider_elem,
                    value_display
                )
            )
        
        return html.div({"class": "flex items-center space-x-3"},
            slider_elem,
            value_display
        )


class Number(Component):
    """Numeric input component"""
    
    def __init__(
        self,
        value: float = 0,
        minimum: Optional[float] = None,
        maximum: Optional[float] = None,
        step: Optional[float] = None,
        label: Optional[str] = None,
        show_label: bool = True,
        interactive: bool = True,
        elem_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            label=label,
            value=value,
            interactive=interactive,
            elem_id=elem_id,
            show_label=show_label,
            **kwargs
        )
        self.minimum = minimum
        self.maximum = maximum
        self.step = step
    
    def render(self) -> Element:
        """Render the number component"""
        props = self.get_props()
        
        input_props = {
            "type": "number",
            "value": str(self.value),
            **({"min": str(self.minimum)} if self.minimum is not None else {}),
            **({"max": str(self.maximum)} if self.maximum is not None else {}),
            **({"step": str(self.step)} if self.step is not None else {}),
            **({"disabled": ""} if not self.interactive else {})
        }
        
        input_elem = html.input({**props, **input_props})
        
        # Add label if needed
        if self.show_label and self.label:
            return html.div({"class": "form-group"},
                html.label({"for": self.elem_id or "number"}, self.label),
                input_elem
            )
        
        return input_elem


class Checkbox(Component):
    """Checkbox component"""
    
    def __init__(
        self,
        value: bool = False,
        label: Optional[str] = None,
        show_label: bool = True,
        interactive: bool = True,
        elem_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            label=label,
            value=value,
            interactive=interactive,
            elem_id=elem_id,
            show_label=show_label,
            **kwargs
        )
    
    def render(self) -> Element:
        """Render the checkbox component"""
        props = self.get_props()
        
        input_props = {
            "type": "checkbox",
            **({"checked": ""} if self.value else {}),
            **({"disabled": ""} if not self.interactive else {})
        }
        
        input_elem = html.input({**props, **input_props})
        
        # Add label if needed
        if self.label:
            return html.div({"class": "form-group"},
                html.label({"class": "checkbox-label"},
                    input_elem,
                    self.label
                )
            )
        
        return input_elem


class Radio(Component):
    """Radio button component"""
    
    def __init__(
        self,
        choices: List[Union[str, Tuple[str, str]]],
        value: Optional[str] = None,
        label: Optional[str] = None,
        show_label: bool = True,
        interactive: bool = True,
        elem_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            label=label,
            value=value,
            interactive=interactive,
            elem_id=elem_id,
            show_label=show_label,
            **kwargs
        )
        self.choices = choices
    
    def render(self) -> Element:
        """Render the radio component"""
        props = self.get_props()
        
        radio_buttons = []
        for i, choice in enumerate(self.choices):
            if isinstance(choice, tuple):
                value, label = choice
            else:
                value = choice
                label = choice
            
            radio_id = f"{self.elem_id or 'radio'}_{i}"
            
            input_props = {
                "type": "radio",
                "name": self.elem_id or "radio",
                "value": value,
                "id": radio_id,
                **({"checked": ""} if self.value == value else {}),
                **({"disabled": ""} if not self.interactive else {})
            }
            
            radio_buttons.append(
                html.div({"class": "radio-option"},
                    html.input(input_props),
                    html.label({"for": radio_id}, label)
                )
            )
        
        # Add label if needed
        if self.show_label and self.label:
            return html.div({"class": "form-group"},
                html.label({"class": "group-label"}, self.label),
                html.div({"class": "radio-group"}, *radio_buttons)
            )
        
        return html.div({"class": "radio-group"}, *radio_buttons)


class Dropdown(Component):
    """Dropdown/select component"""
    
    def __init__(
        self,
        choices: List[Union[str, Tuple[str, str]]],
        value: Optional[str] = None,
        label: Optional[str] = None,
        show_label: bool = True,
        interactive: bool = True,
        elem_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            label=label,
            value=value,
            interactive=interactive,
            elem_id=elem_id,
            show_label=show_label,
            **kwargs
        )
        self.choices = choices
    
    def render(self) -> Element:
        """Render the dropdown component"""
        props = self.get_props()
        
        options = []
        for choice in self.choices:
            if isinstance(choice, tuple):
                value, label = choice
            else:
                value = choice
                label = choice
            
            option_props = {
                "value": value,
                **({"selected": ""} if self.value == value else {})
            }
            
            options.append(html.option(option_props, label))
        
        select_props = {
            **props,
            **({"disabled": ""} if not self.interactive else {})
        }
        
        select_elem = html.select(select_props, *options)
        
        # Add label if needed
        if self.show_label and self.label:
            return html.div({"class": "form-group"},
                html.label({"for": self.elem_id or "dropdown"}, self.label),
                select_elem
            )
        
        return select_elem


class Button(Component):
    """Button component"""
    
    def __init__(
        self,
        value: str = "Button",
        variant: str = "primary",
        size: str = "lg",
        icon: Optional[str] = None,
        link: Optional[str] = None,
        elem_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(value=value, elem_id=elem_id, **kwargs)
        self.variant = variant
        self.size = size
        self.icon = icon
        self.link = link
        self._click_handler = None
    
    def click(self, fn, inputs=None, outputs=None):
        """Add a click event handler to the button"""
        # Normalize inputs and outputs to lists
        if inputs is None:
            inputs = []
        elif not isinstance(inputs, list):
            inputs = [inputs]
            
        if outputs is None:
            outputs = []
        elif not isinstance(outputs, list):
            outputs = [outputs]
            
        self._click_handler = {
            "fn": fn,
            "inputs": inputs,
            "outputs": outputs
        }
        return self
    
    def render(self) -> Element:
        """Render the button component"""
        props = self.get_props()
        
        # Add button classes
        button_classes = ["btn", f"btn-{self.variant}", f"btn-{self.size}"]
        if self.elem_classes:
            button_classes.extend(self.elem_classes)
        props["class_"] = " ".join(button_classes)
        
        # Add click handler if provided
        if self._click_handler:
            props["onclick"] = f"handleButtonClick('{self.elem_id or 'button'}')"
        
        # Add icon if provided
        content = self.value
        if self.icon:
            content = html.span({"class": f"icon-{self.icon}"}, "") + content
        
        # Make it a link if link is provided
        if self.link:
            return html.a({"href": self.link, **props}, content)
        
        return html.button(props, content)


class Label(Component):
    """Label display component"""
    
    def __init__(
        self,
        value: str = "",
        num_top_classes: int = 1,
        label: Optional[str] = None,
        show_label: bool = True,
        elem_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            label=label,
            value=value,
            elem_id=elem_id,
            show_label=show_label,
            **kwargs
        )
        self.num_top_classes = num_top_classes
    
    def render(self) -> Element:
        """Render the label component"""
        props = self.get_props()
        props["class_"] = f"label-display {props.get('class_', '')}"
        
        # Parse the value to extract classes and confidences
        if isinstance(self.value, dict):
            # Handle dictionary format: {"class1": 0.8, "class2": 0.2}
            items = list(self.value.items())
        elif isinstance(self.value, str):
            # Handle string format: "Class1 (0.8), Class2 (0.2)"
            import re
            matches = re.findall(r'([^(]+)\(([^)]+)\)', self.value)
            if matches:
                items = [(cls.strip(), float(conf.strip())) for cls, conf in matches]
            else:
                items = [(self.value, 1.0)]
        else:
            items = [(str(self.value), 1.0)]
        
        # Sort by confidence and limit to top classes
        items.sort(key=lambda x: x[1], reverse=True)
        items = items[:self.num_top_classes]
        
        # Create label elements
        label_elems = []
        for class_name, confidence in items:
            label_elems.append(
                html.div({"class": "label-item"},
                    html.span({"class": "label-name"}, class_name),
                    html.span({"class": "label-confidence"}, f"{confidence:.2f}")
                )
            )
        
        # Add label if needed
        if self.show_label and self.label:
            return html.div({"class": "form-group"},
                html.label({"class": "group-label"}, self.label),
                html.div(props, *label_elems)
            )
        
        return html.div(props, *label_elems)


class Text(Component):
    """Text display component"""
    
    def __init__(
        self,
        value: str = "",
        label: Optional[str] = None,
        show_label: bool = True,
        elem_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            label=label,
            value=value,
            elem_id=elem_id,
            show_label=show_label,
            **kwargs
        )
    
    def render(self) -> Element:
        """Render the text component"""
        props = self.get_props()
        
        # Add Tailwind classes for text display
        base_classes = "p-4 bg-gray-100 rounded-md border border-gray-200 min-h-[60px] text-gray-800"
        if props.get("class_"):
            props["class_"] = f"{base_classes} {props['class_']}"
        else:
            props["class_"] = base_classes
        
        # Add label if needed
        if self.show_label and self.label:
            return html.div({"class": "form-group mb-4"},
                html.label({"class": "block text-sm font-medium text-gray-700 mb-2"}, self.label),
                html.div(props, self.value)
            )
        
        return html.div(props, self.value)


class Image(Component):
    """Image input/output component"""
    
    def __init__(
        self,
        value: Optional[str] = None,
        label: Optional[str] = None,
        show_label: bool = True,
        interactive: bool = True,
        elem_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            label=label,
            value=value,
            interactive=interactive,
            elem_id=elem_id,
            show_label=show_label,
            **kwargs
        )
    
    def render(self) -> Element:
        """Render the image component"""
        props = self.get_props()
        
        if self.interactive:
            # File input for image upload
            input_props = {
                "type": "file",
                "accept": "image/*",
                **props
            }
            
            input_elem = html.input(input_props)
            
            # Add preview if value is provided
            preview = ""
            if self.value:
                preview = html.img({"src": self.value, "class": "image-preview"})
            
            # Add label if needed
            if self.show_label and self.label:
                return html.div({"class": "form-group"},
                    html.label({"for": self.elem_id or "image"}, self.label),
                    input_elem,
                    preview
                )
            
            return html.div({}, input_elem, preview)
        else:
            # Display-only image
            img_props = {
                "src": self.value or "",
                "alt": self.label or "Image",
                **props
            }
            
            # Add label if needed
            if self.show_label and self.label:
                return html.div({"class": "form-group"},
                    html.label({"class": "group-label"}, self.label),
                    html.img(img_props)
                )
            
            return html.img(img_props)


class Row(Component):
    """Row layout component"""
    
    def __init__(
        self,
        *children,
        equal_height: bool = True,
        elem_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(elem_id=elem_id, **kwargs)
        self.children = children
        self.equal_height = equal_height
    
    def render(self) -> Element:
        """Render the row component"""
        props = self.get_props()
        
        # Use Tailwind classes for row layout
        base_classes = "flex flex-row gap-4 mb-4"
        if self.equal_height:
            base_classes += " items-stretch"
        
        if props.get("class_"):
            props["class_"] = f"{base_classes} {props['class_']}"
        else:
            props["class_"] = base_classes
        
        # Convert children to Elements if they aren't already
        child_elements = []
        for child in self.children:
            if isinstance(child, Component):
                child_elements.append(child.render())
            elif isinstance(child, Element):
                child_elements.append(child)
            else:
                child_elements.append(html.div({"class": "flex-1"}, str(child)))
        
        return html.div(props, *child_elements)


class Column(Component):
    """Column layout component"""
    
    def __init__(
        self,
        *children,
        scale: int = 1,
        min_width: int = 160,
        elem_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(elem_id=elem_id, scale=scale, min_width=min_width, **kwargs)
        self.children = children
    
    def render(self) -> Element:
        """Render the column component"""
        props = self.get_props()
        
        # Use Tailwind classes for column layout
        base_classes = "flex flex-col gap-4 mb-4"
        if props.get("class_"):
            props["class_"] = f"{base_classes} {props['class_']}"
        else:
            props["class_"] = base_classes
        
        # Add flex and min-width styles
        style = f"flex: {self.scale}; min-width: {self.min_width}px;"
        if props.get("style"):
            props["style"] = f"{props['style']} {style}"
        else:
            props["style"] = style
        
        # Convert children to Elements if they aren't already
        child_elements = []
        for child in self.children:
            if isinstance(child, Component):
                child_elements.append(child.render())
            elif isinstance(child, Element):
                child_elements.append(child)
            else:
                child_elements.append(html.div({}, str(child)))
        
        return html.div(props, *child_elements)


class Tabs(Component):
    """Tabs container component"""
    
    def __init__(
        self,
        *children,
        elem_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(elem_id=elem_id, **kwargs)
        self.children = children
    
    def render(self) -> Element:
        """Render the tabs component"""
        props = self.get_props()
        props["class_"] = f"tabs {props.get('class_', '')}"
        
        # Extract tab headers and content
        tab_headers = []
        tab_contents = []
        
        for i, child in enumerate(self.children):
            if isinstance(child, Tab):
                tab_id = f"tab-{self.elem_id or 'tabs'}-{i}"
                
                # Create tab header
                header_props = {
                    "class": "tab-header",
                    "data-tab": tab_id,
                    **({"active": ""} if i == 0 else {})
                }
                tab_headers.append(html.div(header_props, child.label))
                
                # Create tab content
                content_props = {
                    "id": tab_id,
                    "class": "tab-content",
                    **({"active": ""} if i == 0 else {})
                }
                
                # Render tab content
                if isinstance(child.content, Component):
                    content_elem = child.content.render()
                elif isinstance(child.content, Element):
                    content_elem = child.content
                else:
                    content_elem = html.div({}, str(child.content))
                
                tab_contents.append(html.div(content_props, content_elem))
        
        return html.div(props,
            html.div({"class": "tab-headers"}, *tab_headers),
            html.div({"class": "tab-contents"}, *tab_contents)
        )


class Tab(Component):
    """Tab content component"""
    
    def __init__(
        self,
        label: str,
        content,
        elem_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(label=label, elem_id=elem_id, **kwargs)
        self.content = content
    
    def render(self) -> Element:
        """Tab components are rendered within Tabs container"""
        return html.div()  # Empty div, actual rendering is done by Tabs


class Chatbot(Component):
    """Chatbot component"""
    
    def __init__(
        self,
        value: Optional[List[Tuple[str, str]]] = None,
        label: Optional[str] = None,
        show_label: bool = True,
        elem_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            label=label,
            value=value or [],
            elem_id=elem_id,
            show_label=show_label,
            **kwargs
        )
    
    def render(self) -> Element:
        """Render the chatbot component"""
        props = self.get_props()
        props["class_"] = f"chatbot {props.get('class_', '')}"
        
        # Create message elements
        message_elements = []
        for user_msg, bot_msg in self.value:
            message_elements.append(
                html.div({"class": "message user-message"},
                    html.div({"class": "message-content"}, user_msg)
                )
            )
            message_elements.append(
                html.div({"class": "message bot-message"},
                    html.div({"class": "message-content"}, bot_msg)
                )
            )
        
        # Add label if needed
        if self.show_label and self.label:
            return html.div({"class": "form-group"},
                html.label({"class": "group-label"}, self.label),
                html.div(props, *message_elements)
            )
        
        return html.div(props, *message_elements)


# Additional components can be added here as needed
class Group(Component):
    """Group component for organizing related components"""
    
    def __init__(
        self,
        *children,
        label: Optional[str] = None,
        show_label: bool = True,
        elem_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            label=label,
            elem_id=elem_id,
            show_label=show_label,
            **kwargs
        )
        self.children = children
    
    def render(self) -> Element:
        """Render the group component"""
        props = self.get_props()
        
        # Use Tailwind classes for group
        base_classes = "p-4 bg-white rounded-lg border border-gray-200 shadow-sm mb-4"
        if props.get("class_"):
            props["class_"] = f"{base_classes} {props['class_']}"
        else:
            props["class_"] = base_classes
        
        # Convert children to Elements if they aren't already
        child_elements = []
        for child in self.children:
            if isinstance(child, Component):
                child_elements.append(child.render())
            elif isinstance(child, Element):
                child_elements.append(child)
            else:
                child_elements.append(html.div({}, str(child)))
        
        # Add label if needed
        if self.show_label and self.label:
            return html.div({"class": "mb-4"},
                html.label({"class": "block text-lg font-semibold text-gray-800 mb-2"}, self.label),
                html.div(props, *child_elements)
            )
        
        return html.div(props, *child_elements)


class Accordion(Component):
    """Accordion component for collapsible content"""
    
    def __init__(
        self,
        *children,
        label: Optional[str] = None,
        open: bool = False,
        elem_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            label=label,
            elem_id=elem_id,
            **kwargs
        )
        self.children = children
        self.open = open
    
    def render(self) -> Element:
        """Render the accordion component"""
        props = self.get_props()
        
        # Use Tailwind classes for accordion
        base_classes = "border border-gray-200 rounded-lg mb-4 overflow-hidden"
        if props.get("class_"):
            props["class_"] = f"{base_classes} {props['class_']}"
        else:
            props["class_"] = base_classes
        
        # Convert children to Elements if they aren't already
        child_elements = []
        for child in self.children:
            if isinstance(child, Component):
                child_elements.append(child.render())
            elif isinstance(child, Element):
                child_elements.append(child)
            else:
                child_elements.append(html.div({}, str(child)))
        
        # Create accordion header with Tailwind classes
        header_classes = "bg-gray-50 px-4 py-3 cursor-pointer hover:bg-gray-100 transition-colors"
        if self.open:
            header_classes += " bg-gray-100"
        
        # Create accordion content with Tailwind classes
        content_classes = "px-4 py-3 bg-white"
        if not self.open:
            content_classes += " hidden"
        
        return html.div(props,
            html.div({"class": header_classes}, 
                html.span({"class": "font-medium text-gray-800"}, self.label or "Accordion")
            ),
            html.div({"class": content_classes}, *child_elements)
        )


# Additional display components
class HTML(Component):
    """Raw HTML display component"""
    
    def __init__(
        self,
        value: str = "",
        label: Optional[str] = None,
        show_label: bool = True,
        elem_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            label=label,
            value=value,
            elem_id=elem_id,
            show_label=show_label,
            **kwargs
        )
    
    def render(self) -> Element:
        """Render the HTML component"""
        props = self.get_props()
        
        # Add label if needed
        if self.show_label and self.label:
            return html.div({"class": "form-group"},
                html.label({"class": "group-label"}, self.label),
                html.div(props, html.raw(self.value))
            )
        
        return html.div(props, html.raw(self.value))


class Markdown(Component):
    """Markdown display component"""
    
    def __init__(
        self,
        value: str = "",
        label: Optional[str] = None,
        show_label: bool = True,
        elem_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            label=label,
            value=value,
            elem_id=elem_id,
            show_label=show_label,
            **kwargs
        )
    
    def render(self) -> Element:
        """Render the Markdown component"""
        props = self.get_props()
        props["class_"] = f"markdown {props.get('class_', '')}"
        
        # For now, just display as preformatted text
        # In a real implementation, you'd want to parse the markdown
        markdown_content = html.pre({}, self.value)
        
        # Add label if needed
        if self.show_label and self.label:
            return html.div({"class": "form-group"},
                html.label({"class": "group-label"}, self.label),
                html.div(props, markdown_content)
            )
        
        return html.div(props, markdown_content)


class JSON(Component):
    """JSON display component"""
    
    def __init__(
        self,
        value: Any = None,
        label: Optional[str] = None,
        show_label: bool = True,
        elem_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            label=label,
            value=value,
            elem_id=elem_id,
            show_label=show_label,
            **kwargs
        )
    
    def render(self) -> Element:
        """Render the JSON component"""
        props = self.get_props()
        props["class_"] = f"json-display {props.get('class_', '')}"
        
        # Format the JSON
        import json
        try:
            formatted_json = json.dumps(self.value, indent=2)
        except (TypeError, ValueError):
            formatted_json = str(self.value)
        
        json_content = html.pre({}, formatted_json)
        
        # Add label if needed
        if self.show_label and self.label:
            return html.div({"class": "form-group"},
                html.label({"class": "group-label"}, self.label),
                html.div(props, json_content)
            )
        
        return html.div(props, json_content)


class Gallery(Component):
    """Gallery component for displaying multiple images"""
    
    def __init__(
        self,
        value: List[str] = None,
        label: Optional[str] = None,
        show_label: bool = True,
        elem_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            label=label,
            value=value or [],
            elem_id=elem_id,
            show_label=show_label,
            **kwargs
        )
    
    def render(self) -> Element:
        """Render the gallery component"""
        props = self.get_props()
        props["class_"] = f"gallery {props.get('class_', '')}"
        
        # Create image elements
        image_elements = []
        for img_src in self.value:
            img_props = {
                "src": img_src,
                "class": "gallery-image",
                "alt": "Gallery image"
            }
            image_elements.append(html.div({"class": "gallery-item"},
                html.img(img_props)
            ))
        
        # Add label if needed
        if self.show_label and self.label:
            return html.div({"class": "form-group"},
                html.label({"class": "group-label"}, self.label),
                html.div(props, *image_elements)
            )
        
        return html.div(props, *image_elements)


class Plot(Component):
    """Plot display component"""
    
    def __init__(
        self,
        value: Any = None,
        label: Optional[str] = None,
        show_label: bool = True,
        elem_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            label=label,
            value=value,
            elem_id=elem_id,
            show_label=show_label,
            **kwargs
        )
    
    def render(self) -> Element:
        """Render the plot component"""
        props = self.get_props()
        props["class_"] = f"plot-display {props.get('class_', '')}"
        
        # For now, just display as a placeholder
        # In a real implementation, you'd want to render the actual plot
        plot_content = html.div({"class": "plot-placeholder"},
            "Plot placeholder - actual plot rendering would go here"
        )
        
        # Add label if needed
        if self.show_label and self.label:
            return html.div({"class": "form-group"},
                html.label({"class": "group-label"}, self.label),
                html.div(props, plot_content)
            )
        
        return html.div(props, plot_content)


# Additional input components
class Audio(Component):
    """Audio input/output component"""
    
    def __init__(
        self,
        value: Optional[str] = None,
        label: Optional[str] = None,
        show_label: bool = True,
        interactive: bool = True,
        elem_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            label=label,
            value=value,
            interactive=interactive,
            elem_id=elem_id,
            show_label=show_label,
            **kwargs
        )
    
    def render(self) -> Element:
        """Render the audio component"""
        props = self.get_props()
        
        if self.interactive:
            # File input for audio upload
            input_props = {
                "type": "file",
                "accept": "audio/*",
                **props
            }
            
            input_elem = html.input(input_props)
            
            # Add player if value is provided
            player = ""
            if self.value:
                player_props = {
                    "src": self.value,
                    "controls": "",
                    "class": "audio-player"
                }
                player = html.audio(player_props)
            
            # Add label if needed
            if self.show_label and self.label:
                return html.div({"class": "form-group"},
                    html.label({"for": self.elem_id or "audio"}, self.label),
                    input_elem,
                    player
                )
            
            return html.div({}, input_elem, player)
        else:
            # Display-only audio player
            audio_props = {
                "src": self.value or "",
                "controls": "",
                "class": "audio-player",
                **props
            }
            
            # Add label if needed
            if self.show_label and self.label:
                return html.div({"class": "form-group"},
                    html.label({"class": "group-label"}, self.label),
                    html.audio(audio_props)
                )
            
            return html.audio(audio_props)


class Video(Component):
    """Video input/output component"""
    
    def __init__(
        self,
        value: Optional[str] = None,
        label: Optional[str] = None,
        show_label: bool = True,
        interactive: bool = True,
        elem_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            label=label,
            value=value,
            interactive=interactive,
            elem_id=elem_id,
            show_label=show_label,
            **kwargs
        )
    
    def render(self) -> Element:
        """Render the video component"""
        props = self.get_props()
        
        if self.interactive:
            # File input for video upload
            input_props = {
                "type": "file",
                "accept": "video/*",
                **props
            }
            
            input_elem = html.input(input_props)
            
            # Add player if value is provided
            player = ""
            if self.value:
                player_props = {
                    "src": self.value,
                    "controls": "",
                    "class": "video-player"
                }
                player = html.video(player_props)
            
            # Add label if needed
            if self.show_label and self.label:
                return html.div({"class": "form-group"},
                    html.label({"for": self.elem_id or "video"}, self.label),
                    input_elem,
                    player
                )
            
            return html.div({}, input_elem, player)
        else:
            # Display-only video player
            video_props = {
                "src": self.value or "",
                "controls": "",
                "class": "video-player",
                **props
            }
            
            # Add label if needed
            if self.show_label and self.label:
                return html.div({"class": "form-group"},
                    html.label({"class": "group-label"}, self.label),
                    html.video(video_props)
                )
            
            return html.video(video_props)


class File(Component):
    """File input component"""
    
    def __init__(
        self,
        value: Optional[str] = None,
        label: Optional[str] = None,
        show_label: bool = True,
        interactive: bool = True,
        elem_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            label=label,
            value=value,
            interactive=interactive,
            elem_id=elem_id,
            show_label=show_label,
            **kwargs
        )
    
    def render(self) -> Element:
        """Render the file component"""
        props = self.get_props()
        
        if self.interactive:
            # File input
            input_props = {
                "type": "file",
                **props
            }
            
            input_elem = html.input(input_props)
            
            # Add label if needed
            if self.show_label and self.label:
                return html.div({"class": "form-group"},
                    html.label({"for": self.elem_id or "file"}, self.label),
                    input_elem
                )
            
            return input_elem
        else:
            # Display file info
            file_info = html.div({"class": "file-info"},
                f"File: {self.value or 'No file'}"
            )
            
            # Add label if needed
            if self.show_label and self.label:
                return html.div({"class": "form-group"},
                    html.label({"class": "group-label"}, self.label),
                    html.div(props, file_info)
                )
            
            return html.div(props, file_info)