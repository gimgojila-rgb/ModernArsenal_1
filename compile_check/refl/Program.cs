using System; using System.IO; using System.Linq; using System.Reflection;
class P { static void Main(string[] a) {
  var root="/mnt/user-data/uploads/tModLoader";
  var dlls=Directory.GetFiles(root,"*.dll",SearchOption.AllDirectories);
  AppDomain.CurrentDomain.AssemblyResolve+=(s,e)=>{var n=new AssemblyName(e.Name).Name+".dll";var f=dlls.FirstOrDefault(d=>Path.GetFileName(d)==n);return f!=null?Assembly.LoadFrom(f):null;};
  var asm=Assembly.LoadFrom(root+"/tModLoader.dll");
  foreach(var tn in a){ var t=asm.GetType(tn); if(t==null){Console.WriteLine("no "+tn);continue;}
    Console.WriteLine("== "+tn);
    foreach(var m in t.GetMembers(BindingFlags.Public|BindingFlags.Instance|BindingFlags.Static|BindingFlags.DeclaredOnly|BindingFlags.NonPublic).Where(m=>!(m is MethodInfo mi && mi.IsSpecialName)))
      try{Console.WriteLine("  "+m.MemberType+" "+(m is MethodInfo mm? mm.ReturnType.Name+" "+m.Name+"("+string.Join(", ",mm.GetParameters().Select(p=>(p.ParameterType.Name)+" "+p.Name))+")": m is FieldInfo fi? fi.FieldType.Name+" "+m.Name : m is PropertyInfo pi? pi.PropertyType.Name+" "+m.Name: m.ToString()));}catch(Exception ex){Console.WriteLine("  ?"+m.Name);}
  }
}}
