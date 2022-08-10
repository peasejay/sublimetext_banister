import sublime
import sublime_plugin
import json
import pickle
import re

class ExampleCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.insert(edit, 0, "Hello, World!")

class MbnRenderTextblocksCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if 'mbn.txt' in self.view.file_name():
            html_filename = self.view.file_name().replace('mbn.txt', 'mbn.html')
            serialized_filename = self.view.file_name().replace('mbn.txt', 'mbn.json')

            # Get the whole document as a region.
            region = sublime.Region(0, self.view.size())

            # Get a list of all lines
            lines = self.view.lines(region)

            text_blocks = {}

            line_count = len(lines)
            prev_line_blank = False

            half_space = '<span class="thin">&nbsp;</span>'
            #one_and_half_space = '<span class="thick">&nbsp;</span>'
            one_and_half_space = '&nbsp;<span class="thin">&nbsp;</span>'

            for line_num, line in enumerate(lines):
                this_line = self.view.substr(line)
                line_length = len(this_line.replace("\n",""))
                if line_num < line_count-1:
                    next_line = self.view.substr(lines[line_num + 1])
                else:
                    next_line = 'no next line'

                if line_length > 0:
                    m = re.search(r"^== (\w+) (\d+)", this_line)
                    if m:
                        textcode = m[1]
                        target_line_length = int(m[2]) 
                        print("Reading block %s (%d)" % (textcode, target_line_length))
                        text_blocks[textcode] = {"target_line_length": target_line_length, "content": ""}
                        prev_line_blank = False
                    else:
                        output_line = this_line
                        # iterate over characters in region and check if we have regions that start or end
                        for pos in range(line.end(), line.begin()-1, -1):
                            line_pos = pos - line.begin()
                            # close out tags, as appropriate
                            for test_region in self.view.get_regions('mbnShortBorder'):
                                if test_region.end() == pos:
                                    output_line = output_line[:line_pos] + half_space + output_line[line_pos+1:]
                            for test_region in self.view.get_regions('mbnStretchBorder'):
                                if test_region.end() == pos:
                                    output_line = output_line[:line_pos] + one_and_half_space + output_line[line_pos+1:]
                            for test_region in self.view.get_regions('mbnUnderline'):
                                if test_region.end() == pos:
                                    output_line = output_line[:line_pos] + '</span>' + output_line[line_pos:]

                            # open tags, as appropriate
                            for test_region in self.view.get_regions('mbnShortExplode'):
                                if test_region.begin() == pos:
                                    temp_string = output_line[line_pos:line_pos+len(test_region)]
                                    temp_string = half_space.join(temp_string[i:i+1] for i in range(0, len(temp_string), 1))
                                    output_line = output_line[:line_pos] + temp_string + output_line[line_pos+len(test_region):]
                            for test_region in self.view.get_regions('mbnUnderline'):
                                if test_region.begin() == pos:
                                    output_line = output_line[:line_pos] + '<span class="underline">' + output_line[line_pos:]
                            for test_region in self.view.get_regions('mbnShortBorder'):
                                if test_region.begin() == pos:
                                    output_line = output_line[:line_pos-1] + half_space + output_line[line_pos:]
                            for test_region in self.view.get_regions('mbnStretchBorder'):
                                if test_region.begin() == pos:
                                    output_line = output_line[:line_pos-1] + one_and_half_space + output_line[line_pos:]

                        if prev_line_blank:
                            output_line = "<p>" + output_line
                        if next_line.replace("\n","") == "":
                            output_line += "</p>"

                        output_line += "\n"

                        text_blocks[textcode]['content'] += output_line

                        prev_line_blank = False
                else:
                    if prev_line_blank:
                        text_blocks[textcode]["content"] += "<p>&nbsp;</p>\n"
                    prev_line_blank = True

            # serialize text blocks to file
            with open(serialized_filename, 'w') as serial_out:
                serial_out.write(json.dumps(text_blocks))

            # serialize text blocks to file
            with open(html_filename, 'w') as html_out:
                html_out.write('<html><head><title>Banister Syles Test</title><link rel="stylesheet" href="styles.css" /></head><body>')

                for key, text_block in text_blocks.items():
                    html_out.write('<div id="%s" class="mbn_text_block">\n' % (key))
                    html_out.write('<p class="text_block_name">Text block: %s (expected length: %s)</p>' % (key, text_block['target_line_length']))
                    html_out.write(text_block['content'])
                    html_out.write('</div>\n\n')


                html_out.write('</body></html>')



            #     line_length = len(line_content.replace("\n",""))

            #     if line_length > 0:
            #         m = re.search(r"^== (\w+) (\d+)", line_content)
            #         if m:
            #             textcode = m[1]
            #             target_line_length = int(m[2]) 
            #             #print("Reading block %s (%d)" % (textcode, target_line_length))
            #             #text_blocks[textcode] = ""
            #             prev_line_blank = False
            #             #output.write('</div>\n\n<div style="font-family: Courier;">\n')
            #         else:
            #             if line_content.replace("\n","") == "":
            #                 continue
            #             else:
            #                 for test_region in self.view.get_regions('mbnShortBorder'):
            #                     if line.contains(test_region):
            #                         line_length -= 1
            #                 for test_region in self.view.get_regions('mbnStretchBorder'):
            #                     if line.contains(test_region):
            #                         line_length += 1
            #                 for test_region in self.view.get_regions('mbnShortExplode'):
            #                     if line.contains(test_region):
            #                         line_length += ((len(test_region) - 1) / 2)
            #                 if line_length == target_line_length:
            #                     regions_good['regions'].append(line)
            #                     regions_good['annotations'].append('Line length: %d (%d)' % (line_length, target_line_length))
            #                 else:
            #                     regions_bad['regions'].append(line)
            #                     regions_bad['annotations'].append('Line length: %d (%d)' % (line_length, target_line_length))                            

            # self.view.add_regions('mbnLineLengthGood', regions_good['regions'], 'region.greenish', 'dot', sublime.HIDDEN, regions_good['annotations'], 'green')
            # self.view.add_regions('mbnLineLengthBad', regions_bad['regions'], 'region.redish', 'dot', sublime.HIDDEN, regions_bad['annotations'], 'red')              


class CalculateMbnLineLengthCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        this_line = self.view.substr(self.view.line(self.view.sel()[0]))
        line_length = len(this_line.replace("\n",""))
        half_spaces = this_line.count('₽')
        one_point_five_spaces = this_line.count('₫')
        line_length -= (half_spaces * .5)
        line_length += (one_point_five_spaces * .5)

        sublime.message_dialog("Line length: %d" % line_length)

class ShowSelectedWordCommand(sublime_plugin.TextCommand):
    def run(self, edit):

        selection = self.view.substr(self.view.sel()[0])
        sublime.message_dialog("Selected word: %s" % selection)


def MbnScanRegions(self, region_name):
    regions = self.view.get_regions(region_name)
    if not regions:
        regions = []

    region_exists = False
    region_index = []
    for index, region in enumerate(regions):
        if region.contains(self.view.sel()[0]):
            region_exists = True
            region_index.append(index)

    if region_exists:
        for index in reversed(region_index):
            del regions[index]
    else:
        regions.append(self.view.sel()[0])

    return regions

def MbnResetRegions(self, region_name):
    regions = self.view.get_regions(region_name)
    if not regions:
        regions = []

    region_exists = False
    region_index = []
    for index, region in enumerate(regions):
        if region.contains(self.view.sel()[0]):
            region_exists = True
            region_index.append(index)

    if region_exists:
        for index in reversed(region_index):
            del regions[index]

    return regions

# counts number of regions in selection
def MbnCountRegions(self, region_name, selection_region):
    regions = self.view.get_regions(region_name)
    region_count = 0
    if not regions:
        regions = []

    region_exists = False
    region_index = []
    for index, region in enumerate(regions):
        if region.contains(self.view.sel()[0]):
            region_exists = True
            region_index.append(index)

    if region_exists:
        for index in reversed(region_index):
            del regions[index]

    return regions

class MbnShowLineLengthCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        this_line = self.view.substr(self.view.line(self.view.sel()[0]))

        codes = [
            'mbnShortExplode', 
            'mbnShortBorder', 
            'mbnStretchBorder',
            ]

        for code in codes:
            pass


        line_length = len(this_line.replace("\n",""))
        half_spaces = this_line.count('₽')
        one_point_five_spaces = this_line.count('₫')
        line_length -= (half_spaces * .5)
        line_length += (one_point_five_spaces * .5)

        sublime.message_dialog("Line length: %d" % line_length)


class MbnAddUnderlineRegionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        code = "mbnUnderline"

        regions = MbnScanRegions(self, code)
        self.view.add_regions(code, regions, 'region.yellowish', flags=sublime.DRAW_SQUIGGLY_UNDERLINE | sublime.DRAW_NO_OUTLINE  | sublime.DRAW_NO_FILL)

class MbnAddShortExplodeRegionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        code = "mbnShortExplode"

        regions = MbnScanRegions(self, code)
        self.view.add_regions(code, regions, 'region.greenish', flags=sublime.DRAW_NO_OUTLINE)

class MbnAddShortBorderRegionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        code = "mbnShortBorder"

        regions = MbnScanRegions(self, code)
        self.view.add_regions(code, regions, 'region.bluish', flags=sublime.DRAW_NO_OUTLINE)

class MbnAddStretchBorderRegionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        code = "mbnStretchBorder"

        regions = MbnScanRegions(self, code)
        self.view.add_regions(code, regions, 'region.purplish', flags=sublime.DRAW_NO_OUTLINE)

class MbnResetRegionsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        codes = {
            'mbnUnderline': {
                'scope': 'region.yellowish',
                'flags': sublime.DRAW_SQUIGGLY_UNDERLINE | sublime.DRAW_NO_OUTLINE  | sublime.DRAW_NO_FILL
                },
            'mbnShortExplode': {
                'scope': 'region.greenish',
                'flags': sublime.DRAW_NO_OUTLINE
                }, 
            'mbnShortBorder': {
                'scope': 'region.bluish',
                'flags': sublime.DRAW_NO_OUTLINE
                }, 
            'mbnStretchBorder': {
                'scope': 'region.purplish',
                'flags': sublime.DRAW_NO_OUTLINE
                }, 
            'MbnRegion': {
                'scope': 'region.reish',
                'flags': sublime.DRAW_NO_OUTLINE
                }, 
            }

        for code, values in codes.items():
            regions = MbnResetRegions(self, code)
            self.view.add_regions(code, regions, values['scope'], flags=values['flags'])


class MbnAddRegionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        code = "MbnRegion"
        regions = MbnScanRegions(self, code)


        self.view.add_regions(code, regions, 'region.redish')

        selection = self.view.substr(self.view.sel()[0])
        sublime.message_dialog("Selected word: %s" % selection)


def MbnImportRegions(view, data_filename):
    codes = {
        'mbnUnderline': {
            'scope': 'region.yellowish',
            'flags': sublime.DRAW_SQUIGGLY_UNDERLINE | sublime.DRAW_NO_OUTLINE  | sublime.DRAW_NO_FILL
            },
        'mbnShortExplode': {
            'scope': 'region.greenish',
            'flags': sublime.DRAW_NO_OUTLINE
            }, 
        'mbnShortBorder': {
            'scope': 'region.bluish',
            'flags': sublime.DRAW_NO_OUTLINE
            }, 
        'mbnStretchBorder': {
            'scope': 'region.purplish',
            'flags': sublime.DRAW_NO_OUTLINE
            }, 
        }

    with open(data_filename, "rb") as f:
        regions = pickle.load(f)

    for code, values in regions.items():
        view.add_regions(code, values, codes[code]['scope'], flags=codes[code]['flags'])

class MbnImportRegionsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if 'mbn.txt' in self.view.file_name():
            data_filename = self.view.file_name().replace('mbn.txt', 'mbn.dat')
            print('Loading MBN regions: %s' % data_filename)
            MbnImportRegions(self.view, data_filename)





        # for code, values in codes.items():
        #     temp = self.view.get_regions(code)
        #     regions[code] = temp

        #     self.view.add_regions(code, regions, codes[code]['scope'], flags=codes[code]['flags'])

        #with open("/Users/jpease/Desktop/regionstest.mbn.txt", "w") as f:
        #    f.write(json.dumps(regions))

class MbnCountJustifiedLineLengthsCommand(sublime_plugin.TextCommand):
    def run(self, edit):

        length_codes = ['mbnLineLengthGood', 'mbnLineLengthBad', 'mbnLineLengthShort']

        # Reset mbn length regions
        for length_code in length_codes:
            self.view.erase_regions(length_code)

        # Get the whole document as a region.
        region = sublime.Region(0, self.view.size())

        # Get a list of all lines
        lines = self.view.lines(region)

        text_blocks = {}
        # target_line_length = 0

        regions_bad = {'regions': [], 'annotations': []}
        regions_good = {'regions': [], 'annotations': []}
        regions_short = {'regions': [], 'annotations': []}

        for line in lines:
            line_content = self.view.substr(line)
            line_length = len(line_content.replace("\n",""))

            if line_length > 0:
                m = re.search(r"^== (\w+) (\d+)", line_content)
                if m:
                    textcode = m[1]
                    target_line_length = int(m[2]) 
                    #print("Reading block %s (%d)" % (textcode, target_line_length))
                    #text_blocks[textcode] = ""
                    prev_line_blank = False
                    #output.write('</div>\n\n<div style="font-family: Courier;">\n')
                else:
                    if line_content.replace("\n","") == "":
                        continue
                    else:
                        for test_region in self.view.get_regions('mbnShortBorder'):
                            if line.contains(test_region):
                                line_length -= 1
                        for test_region in self.view.get_regions('mbnStretchBorder'):
                            if line.contains(test_region):
                                line_length += 1
                        for test_region in self.view.get_regions('mbnShortExplode'):
                            if line.contains(test_region):
                                line_length += ((len(test_region) - 1) / 2)
                        if line_length == target_line_length:
                            regions_good['regions'].append(line)
                            regions_good['annotations'].append('Line length: %d (%d)' % (line_length, target_line_length))
                        elif line_length < target_line_length :
                            regions_short['regions'].append(line)
                            regions_short['annotations'].append('Line length: %d (%d)' % (line_length, target_line_length))
                        else:
                            regions_bad['regions'].append(line)
                            regions_bad['annotations'].append('Line length: %d (%d)' % (line_length, target_line_length))                            

        self.view.add_regions('mbnLineLengthGood', regions_good['regions'], 'region.greenish', 'dot', sublime.HIDDEN, regions_good['annotations'], 'green')
        self.view.add_regions('mbnLineLengthBad', regions_bad['regions'], 'region.redish', 'dot', sublime.HIDDEN, regions_bad['annotations'], 'red')
        self.view.add_regions('mbnLineLengthShort', regions_short['regions'], 'region.orangish', 'dot', sublime.HIDDEN, regions_short['annotations'], 'orange')              

                    


                # half_spaces = this_line.count('₽')
                # one_point_five_spaces = this_line.count('₫')
                # line_length -= (half_spaces * .5)
                # line_length += (one_point_five_spaces * .5)



def MbnExportRegions(view, data_filename):
    codes = {
        'mbnUnderline': {
            'scope': 'region.yellowish',
            'flags': sublime.DRAW_SQUIGGLY_UNDERLINE | sublime.DRAW_NO_OUTLINE  | sublime.DRAW_NO_FILL
            },
        'mbnShortExplode': {
            'scope': 'region.greenish',
            'flags': sublime.DRAW_NO_OUTLINE
            }, 
        'mbnShortBorder': {
            'scope': 'region.bluish',
            'flags': sublime.DRAW_NO_OUTLINE
            }, 
        'mbnStretchBorder': {
            'scope': 'region.purplish',
            'flags': sublime.DRAW_NO_OUTLINE
            }, 
        }

    regions = {}

    for code, values in codes.items():
        temp = view.get_regions(code)
        regions[code] = temp

    with open(data_filename, "wb") as f:
        pickle.dump(regions, f)

class MbnExportRegionsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if 'mbn.txt' in self.view.file_name():
            data_filename = self.view.file_name().replace('mbn.txt', 'mbn.dat')
            print('Exporting MBN regions: %s' % data_filename)
            MbnExportRegions(self.view, data_filename)



class MbnEventListener(sublime_plugin.EventListener):
    @staticmethod
    def on_load(view):
        if 'mbn.txt' in view.file_name():
            data_filename = view.file_name().replace('mbn.txt', 'mbn.dat')
            print('Loading MBN regions: %s' % data_filename)
            MbnImportRegions(view, data_filename)
    @staticmethod
    def on_pre_save(view):
        if 'mbn.txt' in view.file_name():
            data_filename = view.file_name().replace('mbn.txt', 'mbn.dat')
            print('Loading MBN regions: %s' % data_filename)
            MbnExportRegions(view, data_filename)
