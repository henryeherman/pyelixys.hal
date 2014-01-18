#!/usr/bin/env python
"""
The CommandFormat object in cmdfmt.py
parses the sysconf and generates
C source and header files for use on MCUs
that wish to communicate with the 
elixys websocket hardware server
"""
import sys
import struct
import jinja2
from pyelixys.hal.fmt_lookup import fmt_chr
from pyelixys.hal.elixysobject import ElixysObject


class CommandFormatFactory(ElixysObject):
    """ This object generates the header and c file
    for parsing commands from the Elixys INI
    """
    def parse_fmt_str(self):
        fmt_str = "<"  # Little endian
        for key, value in self.sysconf['Commands']['Command Format'].items():
            fmt_str = fmt_str + value
        return fmt_str
        
    def parse_c_struct_def(self):
        struct_val_list = []
        for key, value in self.sysconf['Commands']['Command Format'].items():
            struct_val_list.append((fmt_chr[value], key))
                
        return struct_val_list
    
    def parse_for_cmds(self):
        cmds = [(vals["short_name"] if vals["short_name"] else sec, vals["Commands"]) 
                 for sec, vals in 
                 self.sysconf.items() if "Commands" in
                 vals if vals["Commands"].keys()]        
        return dict(cmds)
        
    def generate_c_header(self,filename=None):
        template_loader = jinja2.FileSystemLoader(searchpath=".")
        template_env = jinja2.Environment(loader=template_loader,
                                          trim_blocks=True,
                                          lstrip_blocks=True)
        TEMPLATE_FILE = self.sysconf['c_cmd_header_template']
        template = template_env.get_template(TEMPLATE_FILE)
        template_vars = {"cmds":self.parse_for_cmds(),
                         "cmdfmt":self.sysconf['Command Format']['Packet Structure'],
                         "fmtchr": fmt_chr,
                         "parameter_sz":self.sysconf['Command Format']['parameter_sz']}        
        output_text = template.render(template_vars)
        
        if filename:
            f = open(filename, "w")
            f.write(output_text)
            f.close()
        
        return output_text

    def generate_c_src(self, filename=None):
        template_loader = jinja2.FileSystemLoader(searchpath=".")
        template_env = jinja2.Environment(loader=template_loader,
                                          trim_blocks=True,
                                          lstrip_blocks=True)
        TEMPLATE_FILE = self.sysconf['c_cmd_source_template']
        template = template_env.get_template(TEMPLATE_FILE)
        template_vars = {}        
        output_text = template.render(template_vars)
        
        if filename:
            f = open(filename, "w")
            f.write(output_text)
            f.close()
        
        return output_text        
        
if __name__ == '__main__':
    cmdfact = CommandFormatFactory()
    #print cmdfact.parse_fmt_str()
    #print cmdfact.parse_c_struct_def()
