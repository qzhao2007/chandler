
void generate_uuid(unsigned char *uuid);
void make_uuid(unsigned char *uuid, char *text, int len);
void format16_uuid(unsigned char *uuid, char *buf);
void format64_uuid(unsigned char *uuid, char *buf);
long hash_uuid(unsigned char *uuid, int len);
