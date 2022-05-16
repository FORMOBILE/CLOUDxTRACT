from tkinter.messagebox import NO
from extractor.data.user import User
import xry
import logging
from extractor.data import File
from functools import lru_cache
from extractor.common import Plugin

logger = logging.getLogger(__name__)


# # In this example we know that the file is a text document so we also give it the Documents view as a parent
# image.relate_nodes(xry.nodeids.views.documents_view, docObject)

# folderNode = image.create_folder(volumeNode, "Download")
# folderNode = image.create_folder(folderNode, "Pictures")

# picObject = image.create_file(folderNode, "MyPicture.jpg")
# image.create_property(picObject, xry.nodeids.views.pictures_view.properties.file_path).set_value("/Download/Pictures/")
# image.create_property(picObject, xry.nodeids.views.pictures_view.properties.raw_data).set_value(bytes.fromhex("89504E470D0A1A0A0000000D49484452000000320000003208060000001E3F88B10000000467414D410000B18F0BFC6105000000206348524D00007A26000080840000FA00000080E8000075300000EA6000003A98000017709CBA513C000000097048597300000EC400000EC401952B0E1B00000006624B474400FF00FF00FFA0BDA7930000002574455874646174653A63726561746500323031392D30322D32355431373A33393A31362B30313A30309C8EAE0B0000002574455874646174653A6D6F6469667900323031392D30322D32355431373A33393A31362B30313A3030EDD316B70000055D494441546843ED9A5B6C54551486FF99E9F432A5AD15D44A5B2FA00D9D12F142BC122F5088F0604C404D7CD244A390185335045F352646C4548CC64B348AD717450D3450625314353E2844D4A9F7006D2D286005A633D3E939FE6BF63A7AD2B433E7CCF46146E723A761ED73D9EBDF7BADB5F7396DC0265086BE038201358A1CF17A6E540D921172703FD0BD1A184FB121A8678A1CDB022AAB8007B602CD14442196DDD51640B8060855E85525C2449A47D2C6A601469284539A332122020CAB523AC4E7D45800C3314909B664F2428E1243C480A960DBA2A10405B8C9CC017F94486AE7A62CA4D8280B2936CA428A8DFFA7108B1B35D9CEFCBB5FCE8E5C971E377B228FB7987BD887F4E507CF42AC093A741238EF2220F1676E31723A710A987336D0780690E4BDB9C4C83393A3C0F98B4C5F7EC47812221DA4E8FCC61F80756F000F6E03460FE9C969184F008B9600EB77001B7601ED57B12DA927A7617488D7F7026B5F377D253D0C98832721321BB3DBD4202DED40EBC5266CA6E3049D5AFDA41AE4D68D6CCB225E9E750E67A2699E3690C616EFB3E249886C9707F701C70F6B035976074387D33F15E2D4FC2B81BAD3B48134CC61C85C36BDF8C409A0F36E35C8510EC46FDFB3EF9036E4C0738E4466033B9F52835C7E3B9D620E4C35F5638CF3CE7BD470D1B98E0EFFA5860B79C6044371F11A6D203BD85784E2BDE2594825DF20F7BCA986B2F42E79B151439150A8E0285E7AB336B858CCD7E910B7DC93C32515E70CF3596E3E7F877D56ABE101CF42326F647C47FE8489E8B0FC3E20FE0747546D21C5915D729B1A244127936C73B8FA1653081CE4DEF851CE169FE5F0F1AB1C0C0E9C9F7725CF4284EA5940FFCB6A9086B3807997302C34EE334E318F563E6C6CA1FF453AE6BA6715CF9DE2358E78B9773E73A79E25DAA1FF15A08A7DF9C19790509849FF2D30F2AB3690550F71C435EE65215B702D63BBCED8C29EB728648B1AA49605207A1D05F05A61EC38857799FF0B233F03C303A6C0F8C19710A18EB3D0F3841AE4DC2B4CD2CB3B6742927CAD691744F4B14156A08374F0476D244D0B4D49975C91AAD4B1424F90ED2CD3B3CE54C307BE85849927FBB6035FBC0B1CF909D87C133B9E6B1CABA098856EA73671764E37E25FB81338CCEBBFFC00F8F4353E87899CE2002C770917F6BE6FFAF08B6F219280B51CB1B7D7038F304446B9FA663ECBD0A9652CAF6EF67E681C96F371AE398F5E0F6C611845241FF89CF831563E9790BEE739180CCB7C3E88F81622483F91462628F751E2A4246E82B1BEC255797A3703359C0DC727B9AEBE8983A06D924FD11B788D2B9F763E6B0A4A3EE425643269EEA124CE65AD71D8CD125A59ABC6148CB1E4DEE84AF203FBB98561290F7A5CC927332342642D71CFC62F9F713B336212792A249F6A39A36DDC483A6C7B8C6D3E56F2C9142C449CAA63CC5FC8EAE5D0F37476A792DC0D2C75EDABD27C5F89F5333F2AB5210F0A1692649277DEAB06912FFAB1DD748A6BCE54FC934FF71B5BD8F50C8B42437E49EE50B010D96E5CC3D2EAD0DBCDDCA89FDE29590817B07AB94FF73DC7953C4B3E79A16021120E037D6A908F5ECABEBD08B27A0D32B11DBEE29A946468050BF424301CB3EDC757B29C729B9ECFCCCA165CB6192D51E0776E2FC0C52CD7F662425675E649D305C0A1184B30B72DF986D54956BF0D3D333023E2400D2BD011BEFD053CFEB248AA5928C2959EF71422C24DC14204714492DB4F78C8B572CF4C8810664448315016526C9485141B6521C5C67F4788D78FC4C58AB82F1A28C48695B132ED25456612E408580836472D6E156CF3CB183696D2213E87AB2D34B7DBE6CF9C0E7C9D46F79A20D2A96049FD9953B86A025DEF5968ED081B216C86850486BE61438928B1F8AFB5639CAF1EF2C503F81B08E3FEA8322938BD0000000049454E44AE426082"))
# image.create_property(picObject, xry.nodeids.views.pictures_view.properties.related_application).set_value("AppName")

# # In this example we know that the file is a picture so we also give it the Pictures view as a parent
# image.relate_nodes(xry.nodeids.views.pictures_view, picObject)


# # Next is a sample of how to add data like accounts, contacts, chat etc.

# # First create the item in the view it should be shown
# accountItem = image.create_item(xry.nodeids.views.accounts_view)
# image.create_property(accountItem, xry.nodeids.views.accounts_view.properties.account_name).set_value("My_account_name")
# image.create_property(accountItem, xry.nodeids.views.accounts_view.properties.display_name).set_value("Sample_name")
# image.create_property(accountItem, xry.nodeids.views.accounts_view.properties.password).set_value("P@55word!")
# image.create_property(accountItem, xry.nodeids.views.accounts_view.properties.created).set_value(datetime.datetime.utcfromtimestamp(1578385457))
# image.create_property(accountItem, xry.nodeids.views.accounts_view.properties.related_application).set_value("AppName")

# # You can relate any item/file to any other item/file so let's relate the picture to this account item
# image.relate_nodes(accountItem, picObject)


class XRYLogfile(Plugin):
    def __init__(self, image):
        self._image = image
        self._volume = None
        self._extractor = None

    def init(self, extractor):
        self._extractor = extractor

    @property
    def volume(self):
        if self._volume is None:
            self._volume = self._image.create_volume(xry.nodeids.roots.volume_root, "/")

        return self._volume

    @lru_cache(maxsize=None)
    def _find_or_create_folder(self, path):
        if path == "":
            return self.volume

        dirs = path.split("/")
        dirname = dirs.pop()
        parent_path = "/".join(dirs)
        parent_node = self._find_or_create_folder(parent_path)
        node = self._image.create_folder(parent_node, dirname)

        return node

    @lru_cache(maxsize=None)
    def _find_or_create_file(self, path):
        dirs = path.split("/")
        filename = dirs.pop()
        parent_path = "/".join(dirs)
        folder_node = self._find_or_create_folder(parent_path)
        file_object = self._image.create_file(folder_node, filename)

        return file_object

    def on_login_success(self, user: User):
        image = self._image
        accountItem = image.create_item(xry.nodeids.views.accounts_view)

        #
        # image.create_property(
        #     accountItem, xry.nodeids.views.accounts_view.properties.account_name
        # ).set_value("My_account_name")

        # Displayname
        if user.displayname is not None:
            image.create_property(
                accountItem, xry.nodeids.views.accounts_view.properties.display_name
            ).set_value(user.displayname)

        # Password
        # image.create_property(
        #     accountItem, xry.nodeids.views.accounts_view.properties.password
        # ).set_value("P@55word!")

        # Account created
        # image.create_property(
        #     accountItem, xry.nodeids.views.accounts_view.properties.created
        # ).set_value(datetime.datetime.utcfromtimestamp(1578385457))

        logger.info("Login successful. %s", user)

    def on_login_failure(self, exception: Exception):
        logger.error("Login failed. %s", exception)

    def on_folder_found(self, folder):
        logger.info("Folder found. %s", folder)

        folder_object = self._find_or_create_folder(folder.path)

        # add properties like created, modified, ...
        if folder.created_at is not None:
            self._image.create_property(
                folder_object, xry.nodeids.views.documents_view.properties.created
            ).set_value(folder.created_at)

    def on_file_found(self, file: File):
        logger.info("File found. %s", file)

        # Create File Handle in Case
        file_object = self._find_or_create_file(file.path)
        self._image.create_property(
            file_object, xry.nodeids.views.documents_view.properties.file_path
        ).set_value(file.path)

        # add aditional properties like created, modified, ...
        if file.created_at is not None:
            self._image.create_property(
                file_object, xry.nodeids.views.documents_view.properties.created
            ).set_value(file.created_at)

        if file.modified_at is not None:
            self._image.create_property(
                file_object, xry.nodeids.views.documents_view.properties.modified
            ).set_value(file.modified_at)

        # Acquire file content
        prop_data = self._image.create_property(file_object, xry.proptypes.raw_data)

        with file as file_stream:
            chunk_size = 4096
            try:
                while True:
                    chunk = file_stream.read(chunk_size)
                    prop_data.write_data(chunk)
                    if len(chunk) < chunk_size:
                        break
            except Exception as ex:
                logger.error("File acquisition error. %s", ex)
            else:
                logger.info("File acquired. %s", file)
